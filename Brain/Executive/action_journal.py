"""Small local audit journal for executive actions (metadata only)."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

JOURNAL = Path(__file__).resolve().parent / "action_journal.jsonl"


def record(action, **fields):
    """Append one event with no prompt text, secrets, or document content."""
    event = {"at": datetime.now(timezone.utc).isoformat(), "action": action}
    event.update({key: value for key, value in fields.items() if value is not None})
    data = (json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(JOURNAL), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        if os.write(fd, data) != len(data):
            raise OSError("Incomplete audit journal write")
        os.fsync(fd)
    finally:
        os.close(fd)
