"""Resolve explicit local note links against known index nodes, read-only."""
import re
import posixpath
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

MAX_NOTES = 1500
MAX_NOTE_BYTES = 2_000_000
MAX_LINKS_PER_NOTE = 150
WIKI = re.compile(r"\[\[([^\]\r\n]{1,240})\]\]")
MARKDOWN = re.compile(r"(?<!!)\[[^\]\r\n]{1,180}\]\(([^)\r\n]{1,300})\)")
_cache = {}


def _key(value):
    return str(value or "").replace("\\", "/").strip().casefold()


def _targets(text):
    for match in WIKI.finditer(text):
        yield match.group(1).split("|", 1)[0].split("#", 1)[0].strip(), "wikilink"
    for match in MARKDOWN.finditer(text):
        target = unquote(match.group(1).split("#", 1)[0].strip())
        if target and not target.lower().startswith(("http:", "https:", "mailto:")):
            yield target, "markdown_link"


def add_note_edges(graph, root):
    """Scan only indexed local Markdown files; skip ambiguous destinations."""
    root = Path(root).resolve()
    nodes, edges = graph.get("nodes"), graph.get("links")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return graph
    paths, names = {}, {}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        relative = _key(node.get("path"))
        if not relative.endswith(".md"):
            continue
        paths.setdefault(relative, set()).add(str(node["id"]))
        for alias in (PurePosixPath(relative).stem, _key(node.get("title"))):
            if alias:
                names.setdefault(alias, set()).add(str(node["id"]))
    existing = {(str(e.get("source")), str(e.get("target")), e.get("relationship"))
                for e in edges if isinstance(e, dict)}
    existing_pairs = {(str(e.get("source")), str(e.get("target")))
                      for e in edges if isinstance(e, dict)}
    added, ambiguous, examined = 0, 0, 0
    for node in nodes:
        if examined >= MAX_NOTES:
            break
        if not isinstance(node, dict):
            continue
        relative = _key(node.get("path"))
        if relative not in paths or not relative.endswith(".md") or relative.startswith("/") or ".." in PurePosixPath(relative).parts:
            continue
        path = root / str(node["path"]).replace("\\", "/")
        try:
            if not path.resolve().is_relative_to(root) or not path.is_file():
                continue
            stat = path.stat()
            if stat.st_size > MAX_NOTE_BYTES:
                continue
            examined += 1
            cache_key = (stat.st_mtime_ns, stat.st_size)
            cached = _cache.get(path)
            if cached is None or cached[0] != cache_key:
                cached = (cache_key, list(_targets(path.read_text(encoding="utf-8-sig", errors="replace")))[:MAX_LINKS_PER_NOTE])
                _cache[path] = cached
        except OSError:
            continue
        for raw, kind in cached[1]:
            target = _key(raw)
            if not target:
                continue
            exact = target if target.endswith(".md") else target + ".md"
            directory = PurePosixPath(relative).parent
            relative_target = posixpath.normpath(_key(directory / exact))
            candidates = paths.get(exact, set()) | paths.get(relative_target, set())
            if not candidates and "/" not in target:
                candidates = names.get(PurePosixPath(target).stem, set())
            if len(candidates) != 1:
                ambiguous += len(candidates) > 1
                continue
            target_id = next(iter(candidates))
            source_id = str(node["id"])
            if source_id == target_id:
                continue
            key = (source_id, target_id, kind)
            if key in existing or (source_id, target_id) in existing_pairs:
                continue
            existing.add(key)
            existing_pairs.add((source_id, target_id))
            edges.append({"source": source_id, "target": target_id,
                          "strength": 1, "relationship": kind, "unresolved": False})
            added += 1
    graph.setdefault("stats", {})["scanned_note_links"] = added
    graph["stats"]["ambiguous_note_links"] = ambiguous
    graph["stats"]["notes_scanned"] = examined
    graph["stats"]["resolved_links"] = sum(1 for e in edges if isinstance(e, dict) and not e.get("unresolved"))
    return graph
