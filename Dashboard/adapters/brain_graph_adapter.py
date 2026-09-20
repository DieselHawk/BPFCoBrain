from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / ".vault-index.json"

def load_index():
    if not INDEX.exists():
        return {}
    try:
        return json.loads(INDEX.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}

def build_brain_graph():
    data = load_index()
    notes = data.get("notes", {})

    if not isinstance(notes, dict):
        notes = {}

    nodes = []
    edges = []
    known = set(notes.keys())

    for node_id, note in notes.items():
        if not isinstance(note, dict):
            continue

        nodes.append({
            "id": node_id,
            "label": note.get("title") or node_id,
            "path": note.get("path", ""),
            "folder": note.get("folder", ""),
            "word_count": int(note.get("word_count", 0) or 0),
            "connection_count": len(note.get("links", []) or []),
            "links": list(note.get("links", []) or [])
        })

        for target in note.get("links", []) or []:
            if target in known:
                edges.append({
                    "source": node_id,
                    "target": target
                })

    unresolved_map = data.get("unresolved_links", {})
    unresolved = (
        sum(len(v) for v in unresolved_map.values() if isinstance(v, list))
        if isinstance(unresolved_map, dict) else 0
    )

    stats = data.get("stats", {})

    return {
        "source": ".vault-index.json",
        "nodes": nodes,
        "links": edges,
        "stats": {
            "notes": len(nodes),
            "words": int(stats.get("total_words", 0) or 0),
            "indexed_connections": int(stats.get("connections", 0) or 0),
            "resolved_links": len(edges),
            "unresolved_links": unresolved
        }
    }
