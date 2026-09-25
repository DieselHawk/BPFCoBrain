"""Bounded, unverified Graphify hints for Fred's local reasoning."""

import json
import os
import re
from collections import defaultdict
from pathlib import Path

from Brain.Executive.source_registry import documents_root

ROOT = Path(__file__).resolve().parents[2]


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


def connection_hints(objective="", limit=60):
    """Share the same saved or folder/title leads with Fred and the 3D display."""
    saved = saved_hints(objective, min(limit, 5))
    if saved:
        return saved
    folder = documents_root()
    if folder is None:
        return []
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
    return [row[4] for row in candidates[:max(0, min(limit, 60))]]
