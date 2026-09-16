from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

ROOT = Path(__file__).resolve().parent
APPROVAL_DIR = ROOT / "Brain" / "Executive" / "Approvals"
PENDING_DIR = APPROVAL_DIR / "Pending"
APPROVED_DIR = APPROVAL_DIR / "Approved"
REJECTED_DIR = APPROVAL_DIR / "Rejected"

for directory in (PENDING_DIR, APPROVED_DIR, REJECTED_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def request(action, agent="Cindy_Secretary", payload=None):
    approval_id = uuid.uuid4().hex
    record = {
        "approval_id": approval_id,
        "agent": agent,
        "action": action,
        "payload": payload or {},
        "status": "pending_human_approval",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    path = PENDING_DIR / f"{approval_id}.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    return record


def is_approved(approval_id):
    return (APPROVED_DIR / f"{approval_id}.json").exists()


def approve(approval_id):
    source = PENDING_DIR / f"{approval_id}.json"

    if not source.exists():
        raise FileNotFoundError(f"Pending approval not found: {approval_id}")

    record = json.loads(source.read_text(encoding="utf-8"))
    record["status"] = "approved"
    record["approved_at"] = datetime.now(timezone.utc).isoformat()

    destination = APPROVED_DIR / source.name
    destination.write_text(json.dumps(record, indent=2), encoding="utf-8")
    source.unlink()

    return record


def reject(approval_id, reason="Rejected by human approver"):
    source = PENDING_DIR / f"{approval_id}.json"

    if not source.exists():
        raise FileNotFoundError(f"Pending approval not found: {approval_id}")

    record = json.loads(source.read_text(encoding="utf-8"))
    record["status"] = "rejected"
    record["rejected_at"] = datetime.now(timezone.utc).isoformat()
    record["reason"] = reason

    destination = REJECTED_DIR / source.name
    destination.write_text(json.dumps(record, indent=2), encoding="utf-8")
    source.unlink()

    return record
