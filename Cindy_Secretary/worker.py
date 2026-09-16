from pathlib import Path
import sys
import json

REPO_ROOT = Path(__file__).resolve().parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_bridge import AgentBridge
from gmail_mailer import GmailMailer
from approval_gate import request, is_approved

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
        "mail", "email", "message", "appointment", "calendar",
        "schedule", "meeting", "admin", "secretary",
        "communication", "contact",
    )

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in source_extensions:
            continue
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if EXECUTIVE_ROOT in path.parents:
            continue
        if any(term in path.name.lower() for term in admin_terms):
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

    return "\n".join([
        "CINDY SECRETARY REVIEW",
        "",
        f"Task: {task.get('objective', 'No objective supplied.')}",
        f"Evidence status: {evidence_status}",
        "",
        "Available administrative evidence:",
        *source_lines,
        "",
        "External capabilities:",
        "Gmail send: APPROVAL REQUIRED",
        "GitHub write: APPROVAL REQUIRED",
        "Human approval gate: ACTIVE",
    ])


def prepare_email(to, subject, body):
    record = request(
        action="gmail.send",
        agent=AGENT,
        payload={
            "to": to,
            "subject": subject,
            "body": body,
        },
    )

    print("CINDY EMAIL PREPARED")
    print(f"Approval ID: {record['approval_id']}")
    print("Status: PENDING HUMAN APPROVAL")
    print("External execution: BLOCKED")


def send_approved_email(approval_id):
    if not is_approved(approval_id):
        raise PermissionError(
            "Human approval required. Gmail send is BLOCKED."
        )

    approval_file = (
        REPO_ROOT / "Brain" / "Executive" /
        "Approvals" / "Approved" / f"{approval_id}.json"
    )

    record = json.loads(
        approval_file.read_text(encoding="utf-8")
    )

    payload = record["payload"]
    result = GmailMailer().send_message(
        payload["to"],
        payload["subject"],
        payload["body"],
    )

    print("CINDY GMAIL SEND COMPLETE")
    print(f"Approval ID: {approval_id}")
    print(f"Message ID: {result.get('id', '<unknown>')}")
    print("Human approval: VERIFIED")


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
    print("Gmail send: APPROVAL REQUIRED")
    print("GitHub write: APPROVAL REQUIRED")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run(sys.argv[1])

    elif len(sys.argv) == 5 and sys.argv[1] == "--prepare-send":
        _, _, to, subject, body_file = sys.argv
        body_path = Path(body_file).expanduser().resolve()

        if not body_path.exists():
            raise SystemExit(f"Body file not found: {body_path}")

        prepare_email(
            to,
            subject,
            body_path.read_text(encoding="utf-8"),
        )

    elif len(sys.argv) == 3 and sys.argv[1] == "--send-approved":
        send_approved_email(sys.argv[2])

    else:
        raise SystemExit(
            "Usage:\n"
            "  python worker.py <task_id>\n"
            "  python worker.py --prepare-send <to> <subject> <body_file>\n"
            "  python worker.py --send-approved <approval_id>"
        )
