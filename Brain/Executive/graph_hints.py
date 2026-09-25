"""Bounded, unverified Graphify hints for Fred's local reasoning."""

import json
import os
import re
import sqlite3
from threading import Lock
from collections import defaultdict
from pathlib import Path

from Brain.Executive.source_registry import documents_root

ROOT = Path(__file__).resolve().parents[2]
_ocr_lock = Lock()


def prepare_fred_hints():
    """Advance local OCR one small batch before Fred reasons; never block on a peer."""
    from Brain.Executive.ocr_runtime import installed_tools
    if installed_tools() is None or not _ocr_lock.acquire(blocking=False):
        return
    try:
        from Brain.Executive.document_lattice import refresh
        refresh(batch=1)
    except (OSError, sqlite3.Error):
        pass  # Cached hints and ordinary evidence remain usable.
    finally:
        _ocr_lock.release()


def saved_hints(objective="", limit=5):
    """Read a saved analysis only; never extract or promote graph edges."""
    root = Path(os.environ.get("BPFCO_GRAPHIFY_ROOT", str(ROOT)))
    candidates = (
        root / "graphify-out" / ".graphify_analysis.json",
        root / ".graphify" / ".graphify_analysis.json",
        root / "00-Inbox" / "workspace" / "obsidian-brain" / "graphify-out" / ".graphify_analysis.json",
        root / "00-Inbox" / "workspace" / "graphify-out" / ".graphify_analysis.json",
    )
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        return []
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig")).get("surprises", [])
    except (OSError, ValueError, AttributeError):
        return []
    if not isinstance(rows, list):
        return []
    terms = set(re.findall(r"[a-z0-9]{4,}", objective.lower())) - {
        "fred", "please", "show", "what", "connection", "connections", "predicted", "prediction", "hints"
    }
    ranked = []
    for item in rows[:100]:
        if not isinstance(item, dict):
            continue
        files = item.get("source_files", [])
        if not isinstance(files, list) or len(files) != 2 or not all(isinstance(f, str) for f in files):
            continue
        source = str(item.get("source", ""))[:100]
        target = str(item.get("target", ""))[:100]
        why = str(item.get("why", ""))[:200]
        haystack = " ".join((source, target, why, *files)).lower()
        matches = sum(term in haystack for term in terms)
        if terms and not matches:
            continue
        ranked.append((matches, {
            "source": source, "target": target, "why": why,
            "confidence": str(item.get("confidence", "unrated"))[:30],
            "source_files": [f[:200] for f in files],
        }))
    ranked.sort(key=lambda pair: -pair[0])
    return [item for _, item in ranked[:max(0, min(limit, 5))]]


def hints_text(objective="", limit=5):
    lines = []
    for item in connection_hints(objective, limit):
        lines.append(
            f"- {item['source']} → {item['target']} ({item['confidence']}): {item['why']} "
            f"[files: {'; '.join(item['source_files'])}]"
        )
    return "\n".join(lines) if lines else "No relevant saved or local document hints."


def extracted_text_hints(folder, objective="", limit=60):
    """Rank cached document text overlap, including optional offline OCR text."""
    catalog = Path(os.environ.get("BPFCO_DOCUMENT_CATALOG", str(ROOT / "Brain" / "cache" / "document_text.sqlite3")))
    if not catalog.is_file():
        return []
    ignore = {"about", "after", "could", "document", "documents", "final", "from",
              "have", "into", "report", "their", "these", "this", "were", "which",
              "with", "would", "your", "there", "shall", "page", "file"}
    try:
        with sqlite3.connect(f"file:{catalog.as_posix()}?mode=ro", uri=True, timeout=2) as db:
            rows = db.execute(
                "SELECT s.path, substr(s.text,1,5000), d.mtime, d.size "
                "FROM document_search AS s JOIN documents AS d ON d.path=s.path "
                "ORDER BY s.path LIMIT 700"
            ).fetchall()
    except (OSError, sqlite3.Error):
        return []
    records = []
    root = folder.resolve()
    for filename, content, mtime, size in rows:
        path = Path(filename)
        try:
            if not path.resolve().is_relative_to(root) or path.is_symlink():
                continue
            stat = path.stat()
            if (stat.st_mtime_ns, stat.st_size) != (mtime, size) or len(content or "") < 50:
                continue
        except OSError:
            continue
        words = set(re.findall(r"[a-z0-9]{5,}", content.lower())) - ignore
        records.append((path, words))
    index = defaultdict(list)
    for number, (_path, words) in enumerate(records):
        for word in words:
            index[word].append(number)
    pairs = defaultdict(set)
    for word, members in index.items():
        if len(members) < 2 or len(members) > max(6, len(records) // 12):
            continue
        for offset, left in enumerate(members):
            for right in members[offset + 1:]:
                pairs[(left, right)].add(word)
    query = set(re.findall(r"[a-z0-9]{5,}", objective.lower())) - ignore
    ranked = []
    for (left, right), shared in pairs.items():
        if len(shared) < 2:
            continue
        a, b = records[left][0], records[right][0]
        if query and not query.intersection(shared | records[left][1] | records[right][1]):
            continue
        terms = sorted(shared)[:5]
        ranked.append((len(shared), str(a), str(b), {
            "source": a.stem[:100], "target": b.stem[:100],
            "why": "Shared extracted text terms: " + ", ".join(terms),
            "confidence": "unverified", "source_files": [str(a), str(b)],
        }))
    ranked.sort(key=lambda row: (-row[0], row[1], row[2]))
    return [row[3] for row in ranked[:max(0, min(limit, 60))]]


def connection_hints(objective="", limit=60):
    """Share the same saved or folder/title leads with Fred and the 3D display."""
    folder = documents_root()
    if folder is None:
        return saved_hints(objective, min(limit, 5))
    content = extracted_text_hints(folder, objective, limit)
    used = {tuple(item["source_files"]) for item in content}
    for item in saved_hints(objective, min(limit, 5)):
        if tuple(item["source_files"]) not in used:
            content.append(item)
            used.add(tuple(item["source_files"]))
    if len(content) >= limit:
        return content[:limit]
    groups = defaultdict(list)
    count = 0
    for current, directories, names in os.walk(folder, followlinks=False):
        depth = len(Path(current).relative_to(folder).parts)
        directories[:] = sorted(d for d in directories if not d.startswith(".") and
                                 not (Path(current) / d).is_symlink()) if depth < 5 else []
        for name in sorted(names):
            path = Path(current) / name
            if path.suffix.lower() not in {".md", ".txt", ".docx", ".pdf"} or path.is_symlink():
                continue
            groups[str(path.parent)].append(path)
            count += 1
            if count >= 1000:
                break
        if count >= 1000:
            break
    ignore = {"document", "documents", "file", "files", "report", "notes", "copy", "final", "draft", "the", "and", "for", "with"}
    terms = set(re.findall(r"[a-z0-9]{4,}", objective.lower())) - ignore - {"fred", "connection", "connections", "predicted", "prediction", "hints"}
    candidates = []
    for parent, members in groups.items():
        for index, a in enumerate(members[:80]):
            a_words = set(re.findall(r"[a-z0-9]{4,}", a.stem.lower())) - ignore
            for b in members[index + 1:80]:
                b_words = set(re.findall(r"[a-z0-9]{4,}", b.stem.lower())) - ignore
                shared = sorted(a_words & b_words)
                reason = f"Same folder: {parent}; " + (
                    f"shared title words: {', '.join(shared)}" if shared else "folder proximity only"
                )
                haystack = f"{a} {b} {reason}".lower()
                matches = sum(term in haystack for term in terms)
                if terms and not matches:
                    continue
                candidates.append((matches, len(shared), str(a), str(b), {
                    "source": a.stem[:100], "target": b.stem[:100],
                    "why": reason[:200], "confidence": "unverified",
                    "source_files": [str(a), str(b)],
                }))
    candidates.sort(key=lambda row: (-row[0], -row[1], row[2], row[3]))
    for row in candidates:
        item = row[4]
        if tuple(item["source_files"]) not in used:
            content.append(item)
            used.add(tuple(item["source_files"]))
        if len(content) >= limit:
            break
    return content
