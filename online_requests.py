"""Local audit trail for agent research requests to Fred.

This module never performs network I/O itself. A caller supplies a read-only
fetch function after selecting an allowed free source.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
REQUEST_DIR = ROOT / "Brain" / "Executive" / "OnlineRequests"
AGENTS = {"Bob_Finance", "Cindy_Secretary", "Kai_Legal", "Neo_Sales"}

def now():
    return datetime.now(timezone.utc).isoformat()

def _write(path, record):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, indent=2), encoding="utf-8")
    temporary.replace(path)

class ResearchRequests:
    def __init__(self, directory=REQUEST_DIR):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def create(self, agent, query, task_id=""):
        if agent not in AGENTS:
            raise ValueError("Unknown requesting agent")
        query = str(query).strip()
        if not 3 <= len(query) <= 1000:
            raise ValueError("Query must be 3 to 1000 characters")
        request_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid4().hex[:8]
        record = {
            "request_id": request_id, "agent": agent, "task_id": str(task_id)[:128],
            "query": query, "status": "requested", "created_at": now(),
            "guidance": "", "source": "", "result": None,
            "external_execution": "research_read_only",
        }
        path = self.directory / (request_id + ".json")
        with path.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
        return record

    def list(self, limit=50):
        records = []
        for path in sorted(self.directory.glob("*.json"), reverse=True)[:max(0, min(limit, 100))]:
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        return records

    def get(self, request_id):
        if not request_id or any(ch not in "0123456789TZ-abcdef" for ch in request_id):
            raise ValueError("Invalid request ID")
        return json.loads((self.directory / (request_id + ".json")).read_text(encoding="utf-8"))

    def guide(self, request_id, guidance):
        record = self.get(request_id)
        if record["status"] != "requested":
            raise ValueError("Only pending requests can be guided")
        guidance = str(guidance).strip()
        if len(guidance) > 1000:
            raise ValueError("Guidance too long")
        record["guidance"] = guidance
        record["guided_at"] = now()
        _write(self.directory / (request_id + ".json"), record)
        return record

    def process(self, request_id, fetch, source, online=None):
        record = self.get(request_id)
        if record["status"] != "requested":
            raise ValueError("Request is not pending")
        active = (os.environ.get("BPFCO_OFFLINE", "1") != "1"
                  and os.environ.get("BPFCO_ONLINE_INTELLIGENCE") == "1")
        if online is False or not active:
            return record
        if not source or len(source) > 200:
            raise ValueError("Source name is required")
        record["status"] = "fetching"
        record["started_at"] = now()
        record["source"] = source
        _write(self.directory / (request_id + ".json"), record)
        try:
            result = fetch(record["query"], record["guidance"])
            if not isinstance(result, dict) or not result.get("source_url"):
                raise ValueError("Research result needs a source_url")
            record["result"] = {
                "source_url": str(result["source_url"])[:500],
                "summary": str(result.get("summary", ""))[:4000],
                "retrieved_at": now(),
            }
            record["status"] = "returned"
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = type(exc).__name__
        record["finished_at"] = now()
        _write(self.directory / (request_id + ".json"), record)
        return record
