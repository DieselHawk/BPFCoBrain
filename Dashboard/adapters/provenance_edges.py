"""Add source provenance edges to an existing Brain graph without changing records."""
import json
from pathlib import Path

MAX_RECORDS = 1000
MAX_RECORD_BYTES = 512_000
MAX_SOURCES_PER_RECORD = 40

def _path(value, root):
    raw = str(value or "").replace("\\", "/").strip()
    base = str(root.resolve()).replace("\\", "/").rstrip("/")
    if raw.casefold().startswith((base + "/").casefold()):
        raw = raw[len(base) + 1:]
    return raw.lstrip("./").casefold()

def _source_path(item):
    if isinstance(item, dict):
        return item.get("path", "")
    return item if isinstance(item, str) else ""

def _records(folder):
    if not folder.is_dir():
        return
    for path in sorted(folder.glob("*.json"))[:MAX_RECORDS]:
        try:
            if path.stat().st_size > MAX_RECORD_BYTES:
                continue
            record = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(record, dict):
                yield path, record
        except (OSError, ValueError):
            continue

def add_provenance_edges(graph, root):
    """Connect task.evidence and report.sources only to known graph nodes."""
    root = Path(root)
    nodes = graph.get("nodes", [])
    edges = graph.get("links", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return graph
    by_path = {}
    for node in nodes:
        if isinstance(node, dict) and node.get("path"):
            by_path[_path(node["path"], root)] = str(node["id"])
    seen = {
        (str(edge.get("source")), str(edge.get("target")), edge.get("relationship"))
        for edge in edges if isinstance(edge, dict)
    }
    added = 0
    for folder, field, relationship in (
        ("tasks", "evidence", "task_evidence"),
        ("reports", "sources", "report_source"),
    ):
        for path, record in _records(root / "Brain" / "Executive" / folder):
            source_id = by_path.get(_path(path, root))
            if source_id is None:
                continue
            items = record.get(field, [])
            if not isinstance(items, list):
                continue
            for item in items[:MAX_SOURCES_PER_RECORD]:
                target_id = by_path.get(_path(_source_path(item), root))
                if target_id is None or target_id == source_id:
                    continue
                key = (source_id, target_id, relationship)
                if key in seen:
                    continue
                seen.add(key)
                edges.append({
                    "source": source_id, "target": target_id,
                    "strength": 1, "relationship": relationship,
                    "unresolved": False,
                })
                added += 1
    graph.setdefault("stats", {})["provenance_links"] = added
    graph["stats"]["resolved_links"] = sum(
        1 for edge in edges if isinstance(edge, dict) and not edge.get("unresolved")
    )
    return graph
