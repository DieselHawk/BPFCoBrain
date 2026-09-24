"""Bounded local evidence lookup over indexed notes and an optional document folder."""

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / ".vault-index.json"
STOP = {"about", "after", "from", "have", "into", "what", "when", "where", "with", "your", "that", "this", "then", "please", "could", "would", "should", "task", "fred", "and", "the", "ingest", "overview"}
EXCLUDED_PARTS = {".git", ".venv", "venv", "node_modules", "site-packages", "vendor", "backups"}
MAX_SOURCE_FILES = 200
MAX_BYTES = 1_000_000

def _external_files():
    configured = os.environ.get("BPFCO_DOCUMENTS_ROOT", "").strip()
    if not configured:
        return
    source = Path(configured).expanduser().resolve()
    if not source.is_dir():
        return
    seen = 0
    for folder, dirs, files in os.walk(source, followlinks=False):
        current = Path(folder)
        depth = len(current.relative_to(source).parts)
        dirs[:] = sorted(d for d in dirs if d.casefold() not in EXCLUDED_PARTS
                         and depth < 3 and not (current / d).is_symlink())
        for name in sorted(files):
            seen += 1
            if seen > MAX_SOURCE_FILES:
                return
            path = current / name
            if path.suffix.lower() in {".md", ".txt"} and not path.is_symlink():
                yield path

def retrieve(objective, limit=4):
    """Return bounded excerpts with source paths; never execute source content."""
    terms = set(re.findall(r"[\w-]{4,}", objective.casefold())) - STOP
    if not terms:
        return []
    try:
        index = json.loads(INDEX.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        index = {}
    candidates = []
    seen_paths = set()
    indexed = []
    for title, meta in index.get("notes", {}).items():
        if not isinstance(meta, dict) or not isinstance(meta.get("path"), str):
            continue
        relative = meta["path"].replace("\\", "/")
        if EXCLUDED_PARTS.intersection(relative.casefold().split("/")):
            continue
        path = (ROOT / relative).resolve()
        if path.is_relative_to(ROOT.resolve()) and path.suffix.lower() == ".md":
            indexed.append((path, str(title), relative))
    for path, title, display in indexed + [
        (p, p.stem, str(p)) for p in _external_files()
    ]:
        if path in seen_paths:
            continue
        seen_paths.add(path)
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            content = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        haystack = content.casefold()
        heading = (title + " " + display).casefold()
        hits = {term for term in terms if term in haystack or term in heading}
        if not hits:
            continue
        content_hits = [haystack.find(term) for term in hits if term in haystack]
        start = max(0, min(content_hits) - 120) if content_hits else 0
        excerpt = " ".join(content[start:start + 650].split())[:650]
        score = len(hits) + 5 * sum(term in heading for term in hits)
        candidates.append((score, title, display, excerpt))
    candidates.sort(key=lambda item: (-item[0], item[2]))
    return [
        {"title": title, "path": display, "excerpt": excerpt}
        for _, title, display, excerpt in candidates[:max(0, min(limit, 20))]
    ]
