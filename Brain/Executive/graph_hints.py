"""Bounded, unverified Graphify hints for Fred's local reasoning."""

import json
import os
import re
from pathlib import Path

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
    for item in saved_hints(objective, limit):
        lines.append(
            f"- {item['source']} → {item['target']} ({item['confidence']}): {item['why']} "
            f"[files: {'; '.join(item['source_files'])}]"
        )
    return "\n".join(lines) if lines else "No relevant saved Graphify hints."
