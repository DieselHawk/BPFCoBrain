"""Expose bounded, read-only document sources and explicit links in the graph."""
import os
from pathlib import Path

from Dashboard.adapters.note_edges import _key, _targets

MAX_DOCUMENTS = 200
MAX_BYTES = 1_000_000
MAX_DEPTH = 3
MAX_LINKS = 100
EXTENSIONS = {".md", ".txt"}


def add_document_edges(graph, root, documents_root=None):
    """Connect only cited sources and unambiguous links; never infer by folder."""
    source = documents_root or os.environ.get("BPFCO_DOCUMENTS_ROOT", "")
    if not source:
        return graph
    folder = Path(source).expanduser().resolve()
    if not folder.is_dir():
        graph.setdefault("stats", {})["document_error"] = "Documents folder unavailable"
        return graph
    nodes, links = graph.get("nodes"), graph.get("links")
    if not isinstance(nodes, list) or not isinstance(links, list):
        return graph
    by_path = {_key(n.get("path")): str(n["id"]) for n in nodes
               if isinstance(n, dict) and n.get("path")}
    discovered = []
    for current, directories, files in os.walk(folder, followlinks=False):
        depth = len(Path(current).relative_to(folder).parts)
        directories[:] = sorted(d for d in directories if not (Path(current) / d).is_symlink()) if depth < MAX_DEPTH else []
        for name in sorted(files):
            if len(discovered) >= MAX_DOCUMENTS:
                break
            path = Path(current) / name
            try:
                if path.suffix.lower() not in EXTENSIONS or path.is_symlink() or path.stat().st_size > MAX_BYTES:
                    continue
                if not path.resolve().is_relative_to(folder):
                    continue
            except OSError:
                continue
            discovered.append(path)
        if len(discovered) >= MAX_DOCUMENTS:
            break
    new_nodes = 0
    for path in discovered:
        key = _key(path)
        if key in by_path:
            continue
        relative = path.relative_to(folder).as_posix()
        node_id = "document:" + relative.casefold()
        if any(str(node.get("id")) == node_id for node in nodes if isinstance(node, dict)):
            continue
        nodes.append({"id": node_id, "label": path.stem, "title": path.stem,
                      "path": str(path), "folder": "Documents / " + str(path.relative_to(folder).parent),
                      "word_count": 0, "connection_count": 0, "links": [], "content": "", "frontmatter": {}})
        by_path[key] = node_id
        new_nodes += 1
    unique_names = {}
    for node in nodes:
        if not isinstance(node, dict) or not node.get("path"):
            continue
        path = Path(str(node["path"]))
        if path.suffix.lower() in EXTENSIONS:
            unique_names.setdefault(path.stem.casefold(), set()).add(str(node["id"]))
    seen = {(str(e.get("source")), str(e.get("target"))) for e in links if isinstance(e, dict)}
    new_edges = 0
    for path in discovered:
        source_id = by_path.get(_key(path))
        try:
            raw = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        for target, relationship in list(_targets(raw))[:MAX_LINKS]:
            target = target.strip()
            if not target:
                continue
            candidates = set()
            candidate = (path.parent / target).resolve()
            candidates.update([by_path[_key(candidate)]] if _key(candidate) in by_path else [])
            if not candidates and "/" not in target and "\\" not in target:
                candidates = unique_names.get(Path(target).stem.casefold(), set())
            if len(candidates) != 1:
                continue
            target_id = next(iter(candidates))
            if source_id == target_id or (source_id, target_id) in seen:
                continue
            seen.add((source_id, target_id))
            links.append({"source": source_id, "target": target_id,
                          "relationship": "document_" + relationship,
                          "strength": 1, "unresolved": False})
            new_edges += 1
    graph.setdefault("stats", {})["document_sources"] = len(discovered)
    graph["stats"]["document_nodes"] = new_nodes
    graph["stats"]["document_links"] = new_edges
    graph["stats"]["resolved_links"] = sum(1 for e in links if isinstance(e, dict) and not e.get("unresolved"))
    return graph
