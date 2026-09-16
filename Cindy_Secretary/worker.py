from pathlib import Path
import sys
import json

# Make the BPFCoBrain root available when launched directly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_bridge import AgentBridge

AGENT = "Cindy_Secretary"
BRAIN_ROOT = REPO_ROOT / "Brain"
EXECUTIVE_ROOT = BRAIN_ROOT / "Executive"


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def inspect_admin_sources():
    findings = []

    source_extensions = {".json", ".md", ".txt", ".csv"}

    admin_terms = (
        "mail",
        "email",
        "message",
        "appointment",
        "calendar",
        "schedule",
        "meeting",
        "admin",
        "secretary",
        "communication",
        "contact",
    )

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in source_extensions:
            continue

        if ".git" in path.parts or "__pycache__" in path.parts:
            continue

        # Executive files are control/state records, not communication evidence.
        if EXECUTIVE_ROOT in path.parents:
            continue

        name = path.name.lower()

        if any(term in name for term in admin_terms):
            findings.append({
                "file": str(path),
                "size": path.stat().st_size,
            })

    return findings


def build_secretary_review(task):
    sources = inspect_admin_sources()

    if sources:
        source_lines = [
            f"- {item['file']} ({item['size']} bytes)"
            for item in sources
        ]
        evidence_status = "Administrative or communication source files detected."
    else:
        source_lines = [
            "- No verified message, email, appointment, calendar, "
            "meeting, or scheduling source files were found."
        ]
        evidence_status = "No administrative/scheduling source data is currently available."

    review = [
        "CINDY SECRETARY INTERNAL REVIEW",
        "",
        f"Task: {task.get('objective', 'No objective supplied.')}",
        f"Evidence status: {evidence_status}",
        "",
        "Available administrative evidence:",
        *source_lines,
        "",
        "Priority assessment:",
        "No messages, appointments, meetings, or scheduling priorities "
        "were inferred because no verified administrative source data "
        "was found.",
        "",
        "Required next input:",
        "Administrative records, communication exports, calendar data, "
        "or scheduling documents can be indexed into the Brain before "
        "Cindy performs substantive prioritisation.",
        "",
        "External execution:",
        "BLOCKED pending user approval.",
    ]

    return "\n".join(review)


def run(task_id):
    bridge = AgentBridge()

    task = bridge.claim(task_id, AGENT)

    review = build_secretary_review(task)

    report = bridge.complete(
        task_id,
        AGENT,
        review,
        status="complete",
    )

    print(f"{AGENT} WORKER COMPLETE")
    print(f"Task: {task_id}")
    print(f"Report: {report.get('task_id', task_id)}")
    print("Returned to CEO: YES")
    print("Administrative evidence fabricated: NO")
    print("External execution: BLOCKED pending user approval")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python worker.py <task_id>")

    run(sys.argv[1])
