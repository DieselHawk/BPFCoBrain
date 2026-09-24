"""Add source provenance edges to an existing Brain graph without changing records."""
import json
import re
from pathlib import Path

MAX_RECORDS = 1000
MAX_RECORD_BYTES = 512_000
MAX_SOURCES_PER_RECORD = 40
MAX_EXPERIENCES = 300
MAX_EXPERIENCE_BYTES = 64_000
TASK_ID_LINE = re.compile(r"^\*\*Task ID\*\*:\s*([A-Za-z0-9_-]{8,120})\s*$", re.MULTILINE)

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
    def connect(source_id, target_id, relationship):
        nonlocal added
        if target_id is None or target_id == source_id:
            return
        key = (source_id, target_id, relationship)
        if key in seen:
            return
        seen.add(key)
        edges.append({
            "source": source_id, "target": target_id,
            "strength": 1, "relationship": relationship,
            "unresolved": False,
        })
        added += 1

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
                connect(source_id, target_id, relationship)

    # Experience notes carry an explicit task ID. Attach them only to task and
    # report nodes already present in the graph; never infer a match by title.
    experiences = root / "Brain" / "Executive" / "Experience"
    if experiences.is_dir():
        for path in sorted(experiences.glob("*.md"))[:MAX_EXPERIENCES]:
            try:
                if path.stat().st_size > MAX_EXPERIENCE_BYTES:
                    continue
                match = TASK_ID_LINE.search(path.read_text(encoding="utf-8-sig")[:2048])
            except (OSError, UnicodeError):
                continue
            if match is None:
                continue
            task_id = match.group(1)
            targets = (
                (by_path.get(_path(root / "Brain" / "Executive" / "tasks" / (task_id + ".json"), root)), "experience_task"),
                (by_path.get(_path(root / "Brain" / "Executive" / "reports" / (task_id + ".json"), root)), "experience_report"),
            )
            if not any(target for target, _ in targets):
                continue
            relative = path.relative_to(root).as_posix()
            source_id = by_path.get(_path(relative, root))
            if source_id is None:
                source_id = "experience:" + relative
                if any(str(node.get("id")) == source_id for node in nodes if isinstance(node, dict)):
                    continue
                nodes.append({"id": source_id, "label": path.stem,
                              "title": path.stem, "path": relative,
                              "folder": "Executive / Experience",
                              "word_count": 0, "connection_count": 0,
                              "links": [], "content": "", "frontmatter": {}})
                by_path[_path(relative, root)] = source_id
            for target_id, relationship in targets:
                connect(source_id, target_id, relationship)
    graph.setdefault("stats", {})["provenance_links"] = added
    graph["stats"]["resolved_links"] = sum(
        1 for edge in edges if isinstance(edge, dict) and not edge.get("unresolved")
    )
    return graph
