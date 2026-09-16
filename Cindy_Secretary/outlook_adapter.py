from pathlib import Path
import json
from approval_gate import request, is_approved

ROOT = Path(__file__).resolve().parent.parent
APPROVAL_ROOT = ROOT / "Brain" / "Executive" / "Approvals"


def prepare_outlook_send(to, subject, body):
    record = request(
        action="outlook.send",
        agent="Cindy_Secretary",
        payload={
            "to": to,
            "subject": subject,
            "body": body,
        },
    )

    print("CINDY OUTLOOK ACTION PREPARED")
    print(f"Approval ID: {record['approval_id']}")
    print("Action: outlook.send")
    print("Status: PENDING HUMAN APPROVAL")
    print("External execution: BLOCKED")

    return record


def get_approved_action(approval_id):
    if not is_approved(approval_id):
        raise PermissionError(
            "Human approval required. Outlook send is BLOCKED."
        )

    path = (
        APPROVAL_ROOT /
        "Approved" /
        f"{approval_id}.json"
    )

    return json.loads(path.read_text(encoding="utf-8"))


def describe_approved_outlook_send(approval_id):
    record = get_approved_action(approval_id)

    if record.get("action") != "outlook.send":
        raise PermissionError(
            "Approval is not for an Outlook send action."
        )

    payload = record["payload"]

    print("CINDY OUTLOOK APPROVAL VERIFIED")
    print(f"Approval ID: {approval_id}")
    print(f"To: {payload['to']}")
    print(f"Subject: {payload['subject']}")
    print("Human approval: VERIFIED")
    print("Connector execution: READY")
    print("Actual send: NOT PERFORMED BY LOCAL TEST")


if __name__ == "__main__":
    print("Cindy Outlook adapter loaded.")
