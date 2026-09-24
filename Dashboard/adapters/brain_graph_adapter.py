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
    index = load_index()
    notes = index.get("notes", {})

    if not isinstance(notes, dict):
        notes = {}

    nodes = []
    links = []
    known = {str(k).lower(): k for k in notes.keys()}

    for node_id, note in notes.items():
        if not isinstance(note, dict):
            continue

        targets = index.get("graph", {}).get(node_id)
        if not isinstance(targets, list) or not targets:
            targets = note.get("links", [])

        node_links = list(targets or [])

        nodes.append({
            "id": str(node_id),
            "label": note.get("title") or str(node_id),
            "title": note.get("title") or str(node_id),
            "path": note.get("path", ""),
            "folder": note.get("folder", ""),
            "word_count": int(note.get("word_count", 0) or 0),
            "connection_count": len(node_links),
            "links": node_links,
            "content": note.get("content", ""),
            "frontmatter": note.get("frontmatter", {})
        })

    existing_ids = {n["id"] for n in nodes}
    unresolved = {}

    for node in list(nodes):
        for target in node["links"]:
            target_text = str(target)
            target_id = known.get(target_text.lower())

            if target_id is None:
                external_id = f"external:{target_text}"
                if external_id not in existing_ids:
                    existing_ids.add(external_id)
                    nodes.append({
                        "id": external_id,
                        "label": f"[unresolved] {target_text}",
                        "title": f"[unresolved] {target_text}",
                        "path": "",
                        "folder": "unresolved",
                        "word_count": 0,
                        "connection_count": 0,
                        "links": [],
                        "content": "",
                        "frontmatter": {},
                        "unresolved": True
                    })
                target_id = external_id
                unresolved[target_text] = unresolved.get(target_text, 0) + 1

            key = tuple(sorted((node["id"], target_id)))
            if not hasattr(build_brain_graph, "_seen"):
                build_brain_graph._seen = set()

            if key not in build_brain_graph._seen:
                build_brain_graph._seen.add(key)
                links.append({
                    "source": node["id"],
                    "target": target_id,
                    "strength": 1,
                    "unresolved": target_id.startswith("external:")
                })

    # Reset duplicate-protection between calls.
    build_brain_graph._seen = set()

    # Executive records have explicit task and agent IDs. Keep these edges
    # distinct from the note links inferred from the vault index.
    executive = ROOT / "Brain" / "Executive"
    agent_ids = set()
    task_ids = set()
    report_count = 0
    executive_links = 0

    def connect(source, target, relationship):
        nonlocal executive_links
        links.append({"source": source, "target": target,
                      "strength": 1, "relationship": relationship,
                      "unresolved": False})
        executive_links += 1

    def agent_node(name):
        if not name or name in agent_ids:
            return
        agent_ids.add(name)
        nodes.append({"id": f"agent:{name}", "label": name,
                      "title": name, "folder": "Executive / Agents",
                      "path": "", "word_count": 0, "connection_count": 2,
                      "links": [], "content": "", "frontmatter": {},
                      "kind": "agent"})

    for folder, kind in (("tasks", "task"), ("reports", "report")):
        for path in sorted((executive / folder).glob("*.json")):
            try:
                record = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError):
                continue
            if not isinstance(record, dict):
                continue
            task_id = record.get("task_id")
            agent = record.get("agent")
            if not isinstance(task_id, str) or not task_id or not isinstance(agent, str) or not agent:
                continue
            agent_node(agent)
            if kind == "task":
                task_ids.add(task_id)
            else:
                report_count += 1
            node_id = f"{kind}:{task_id}"
            nodes.append({"id": node_id,
                          "label": (record.get("objective") or task_id) if kind == "task" else f"Report: {agent}",
                          "title": task_id, "path": str(path.relative_to(ROOT)),
                          "folder": f"Executive / {folder.title()}",
                          "word_count": 0, "connection_count": 1,
                          "links": [], "content": "", "frontmatter": {},
                          "kind": kind, "status": record.get("status", "")})
            if kind == "task":
                connect(f"agent:{agent}", node_id, "assigned")
            elif task_id in task_ids:
                connect(f"task:{task_id}", node_id, "reported")
            else:
                connect(f"agent:{agent}", node_id, "reported")

    # If report files sort before their task files on a future refactor,
    # the task loop above still runs first by design.

    stats = index.get("stats", {})
    if not isinstance(stats, dict):
        stats = {}

    total_words = stats.get("total_words", 0)
    total_notes = stats.get("total_notes", len([n for n in nodes if not n.get("unresolved")]))
    indexed_connections = stats.get("connections", 0)

    return {
        "source": ".vault-index.json",
        "nodes": nodes,
        "links": links,
        "stats": {
            "notes": int(total_notes or 0),
            "words": int(total_words or 0),
            "indexed_connections": int(indexed_connections or 0),
            "resolved_links": sum(1 for x in links if not x["unresolved"]),
            "unresolved_links": sum(1 for x in links if x["unresolved"]),
            "executive_reports": report_count,
            "executive_links": executive_links
        }
    }
