import json
from datetime import datetime, timezone
from pathlib import Path
from Brain.Executive.local_evidence import retrieve

ROOT = Path(__file__).resolve().parent
EXECUTIVE_DIR = ROOT / "Brain" / "Executive"
TASK_DIR = EXECUTIVE_DIR / "tasks"
REPORT_DIR = EXECUTIVE_DIR / "reports"
QUEUE_FILE = EXECUTIVE_DIR / "queue.json"
SHARED_CONTEXT_FILE = EXECUTIVE_DIR / "shared_context.json"

AGENTS = {
    "Fred",
    "Bob_Finance",
    "Cindy_Secretary",
    "Kai_Legal",
    "Neo_Sales",
}


def now():
    return datetime.now(timezone.utc).isoformat()


class AgentBridge:
    def __init__(self):
        TASK_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

    def _load_shared_context(self):
        if not SHARED_CONTEXT_FILE.exists():
            return {}
        try:
            return json.loads(SHARED_CONTEXT_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _load_json(self, path, default=None):
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            return default if default is not None else {}

    def _load_queue(self):
        if not QUEUE_FILE.exists():
            return []
        try:
            return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_queue(self, queue):
        QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")

    def dispatch(self, agent, objective, priority="normal", approval_required=True):
        if agent not in AGENTS:
            raise ValueError(f"Unknown specialist agent: {agent}")

        # Defense-in-depth: never create a second active task for
        # the same agent and objective. Task records are authoritative.
        for existing_path in TASK_DIR.glob("*.json"):
            existing = self._load_json(existing_path, {})
            if (
                existing.get("agent") == agent
                and existing.get("objective") == objective
                and existing.get("status") in {"queued", "in_progress"}
            ):
                return existing

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        task_id = f"{stamp}-{agent}"

        task = {
            "task_id": task_id,
            "created_at": now(),
            "created_by": "Human" if agent == "Fred" else "CEO",
            "agent": agent,
            "objective": objective,
            "priority": priority,
            "status": "queued",
            "approval_required_before_external_execution": bool(approval_required),
            "execution_mode": "internal_only",
            "shared_context": self._load_shared_context(),
            "evidence": retrieve(objective),
        }

        (TASK_DIR / f"{task_id}.json").write_text(
            json.dumps(task, indent=2),
            encoding="utf-8",
        )

        queue = self._load_queue()
        queue.append({
            "task_id": task_id,
            "agent": agent,
            "status": "queued",
        })
        self._save_queue(queue)
        return task

    def claim(self, task_id, agent):
        path = TASK_DIR / f"{task_id}.json"

        if not path.exists():
            raise FileNotFoundError(task_id)

        task = json.loads(path.read_text(encoding="utf-8"))

        if task["agent"] != agent:
            raise PermissionError("Task belongs to a different agent")

        if task["status"] != "queued":
            raise ValueError(f"Task is {task['status']}, not queued")

        task["status"] = "in_progress"
        task["claimed_at"] = now()

        path.write_text(
            json.dumps(task, indent=2),
            encoding="utf-8",
        )
        return task

    def complete(self, task_id, agent, summary, status="complete", sources=None):
        path = TASK_DIR / f"{task_id}.json"

        if not path.exists():
            raise FileNotFoundError(task_id)

        task = json.loads(path.read_text(encoding="utf-8"))

        if task["agent"] != agent:
            raise PermissionError("Task belongs to a different agent")

        if task["status"] not in {"queued", "in_progress"}:
            raise ValueError(f"Task is {task['status']}")

        task["status"] = status
        task["completed_at"] = now()

        path.write_text(
            json.dumps(task, indent=2),
            encoding="utf-8",
        )

        report = {
            "task_id": task_id,
            "agent": agent,
            "reported_at": now(),
            "status": status,
            "summary": summary,
            "returned_to": "Human" if agent == "Fred" else "CEO",
            "external_execution": "blocked_pending_user_approval",
            "shared_context_attached": bool(task.get("shared_context")),
        }
        if sources is not None:
            report["sources"] = sources

        (REPORT_DIR / f"{task_id}.json").write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )

        queue = [
            item
            for item in self._load_queue()
            if item["task_id"] != task_id
        ]
        self._save_queue(queue)

        return report

    def pending(self):
        return self._load_queue()


def self_test():
    bridge = AgentBridge()

    task = bridge.dispatch(
        "Neo_Sales",
        "SELF-TEST: verify CEO-to-agent task dispatch.",
        priority="test",
    )

    bridge.claim(task["task_id"], "Neo_Sales")

    report = bridge.complete(
        task["task_id"],
        "Neo_Sales",
        "Bridge task received and report returned to CEO.",
    )

    print("=== BPFCoBrain AGENT BRIDGE SELF-TEST ===")
    print("Dispatch: OK")
    print("Agent claim: OK")
    print("Report return to CEO: OK")
    print(f"Approval gate: {report['external_execution']}")
    print(f"Pending queue: {len(bridge.pending())}")
    print("SELF-TEST COMPLETE")


if __name__ == "__main__":
    self_test()
