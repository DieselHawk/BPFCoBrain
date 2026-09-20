from pathlib import Path
from datetime import datetime, timezone
import json
import uuid
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
APPROVAL_DIR = ROOT / "Brain" / "Executive" / "Approvals"
PENDING_DIR = APPROVAL_DIR / "Pending"
APPROVED_DIR = APPROVAL_DIR / "Approved"
REJECTED_DIR = APPROVAL_DIR / "Rejected"


# BPFCO_APPROVAL_SECURITY_V1
BPFCO_APPROVAL_USB = os.environ.get("BPFCO_APPROVAL_USB", r"E:\")

def _usb_token_valid(usb_path=None):
    usb = usb_path or BPFCO_APPROVAL_USB
    verifier = ROOT / "Brain" / "Security" / "bpfco_security.py"

    if not verifier.exists():
        return False

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(verifier),
                "verify",
                "--usb",
                usb,
            ],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(ROOT),
        )
        return result.returncode == 0
    except Exception:
        return False

def security_status():
    return {
        "usb_required": True,
        "usb_path": BPFCO_APPROVAL_USB,
        "usb_valid": _usb_token_valid(),
        "human_terminal_required": True,
        "external_execution": "BLOCKED_UNTIL_APPROVED",
    }

def _require_human_terminal(approval_id):
    if not sys.stdin.isatty():
        raise PermissionError(
            "BPFCo approval rejected: interactive human terminal required."
        )

    print("")
    print("=== BPFCo HUMAN APPROVAL ===")
    print(f"Approval ID: {approval_id}")
    print("USB cryptographic token: VALID")
    print("Press ENTER to approve.")
    input()

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

    # Security order is deliberate:
    # 1. Valid BPFCo USB token
    # 2. Human terminal confirmation
    # 3. Only then create Approved record
    if not _usb_token_valid():
        raise PermissionError(
            "BPFCo approval rejected: valid USB cryptographic token required."
        )

    _require_human_terminal(approval_id)

    record = json.loads(source.read_text(encoding="utf-8"))
    record["status"] = "approved"
    record["approved_at"] = datetime.now(timezone.utc).isoformat()
    record["approved_by"] = "human_terminal"
    record["approval_method"] = "bpfco_usb_token_plus_enter"

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

