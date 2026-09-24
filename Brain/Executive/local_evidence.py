"""Small, offline evidence lookup over the existing vault index."""

import json
import os
import re
from pathlib import Path
from Brain.Executive.source_registry import documents_root


ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / ".vault-index.json"
STOP = {"about", "after", "from", "have", "into", "what", "when", "where", "with", "your", "that", "this", "then", "please", "could", "would", "should", "task", "fred", "and", "the"}
EXCLUDED_PARTS = {".git", ".venv", "venv", "node_modules", "site-packages", "vendor"}


def document_candidates(terms):
    """Read a bounded, local sample. Missing extractors simply skip PDFs."""
    folder = documents_root()
    if folder is None:
        return []
    from Dashboard.adapters.document_edges import _docx_text, _pdf_text
    candidates = []
    examined = 0
    pdf_count = 0
    for current, directories, names in os.walk(folder, followlinks=False):
        depth = len(Path(current).relative_to(folder).parts)
        directories[:] = sorted(d for d in directories if not d.startswith('.') and
                                not (Path(current) / d).is_symlink()) if depth < 5 else []
        for name in sorted(names):
            if examined >= 100:
                return candidates
            path = Path(current) / name
            if path.suffix.lower() not in {'.md', '.txt', '.docx', '.pdf'} or path.is_symlink():
                continue
            try:
                if not path.resolve().is_relative_to(folder) or path.stat().st_size > 2_000_000:
                    continue
                examined += 1
                if path.suffix.lower() == '.docx':
                    content = _docx_text(path)
                elif path.suffix.lower() == '.pdf':
                    if pdf_count >= 8:
                        continue
                    pdf_count += 1
                    content = _pdf_text(path)
                else:
                    content = path.read_text(encoding='utf-8-sig', errors='replace')[:150_000]
            except Exception:
                continue
            if not content:
                continue
            haystack = content.casefold()
            hits = {term for term in terms if term in haystack}
            if not hits:
                continue
            heading = path.name.casefold()
            score = len(hits) + 5 * sum(term in heading for term in hits)
            first = min(haystack.find(term) for term in hits)
            excerpt = ' '.join(content[max(0, first - 120):first + 520].split())[:650]
            candidates.append((score, path.stem, str(path), excerpt))
    return candidates


def retrieve(objective, limit=4):
    """Return short excerpts with paths; never execute content from notes."""
    try:
        index = json.loads(INDEX.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        index = {}
    terms = set(re.findall(r"[\w-]{4,}", objective.casefold())) - STOP
    if not terms:
        return []

    candidates = []
    for title, meta in index.get("notes", {}).items():
        if not isinstance(meta, dict):
            continue
        path = meta.get("path", "")
        if not isinstance(path, str) or not path:
            continue
        normalized_path = path.replace("\\", "/")
        if EXCLUDED_PARTS.intersection(normalized_path.casefold().split("/")):
            continue
        file_path = (ROOT / normalized_path).resolve()
        if not file_path.is_relative_to(ROOT.resolve()) or file_path.suffix.lower() != ".md":
            continue
        try:
            if file_path.stat().st_size > 1_000_000:
                continue
            content = file_path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        haystack = content.casefold()
        hits = {term for term in terms if term in haystack}
        if not hits:
            continue
        heading = (str(title) + " " + path).casefold()
        score = len(hits) + 5 * sum(term in heading for term in hits)
        first = min(haystack.find(term) for term in hits)
        start = max(0, first - 120)
        excerpt = " ".join(content[start:first + 520].split())[:650]
        candidates.append((score, str(title), normalized_path, excerpt))

    candidates.extend(document_candidates(terms))
    candidates.sort(key=lambda item: (-item[0], item[2]))
    return [
        {"title": title, "path": path, "excerpt": excerpt}
        for _, title, path, excerpt in candidates[:limit]
    ]
