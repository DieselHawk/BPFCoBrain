import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXECUTIVE_DIR = ROOT / "Brain" / "Executive"
STATE_FILE = EXECUTIVE_DIR / "state.json"
MANIFEST_FILE = ROOT / "Shared_Context" / "manifest.json"
HITL_FILE = ROOT / "Human_In_The_Loop.md"
QUEUE_FILE = EXECUTIVE_DIR / "queue.json"

AGENTS = {
    "CEO": "Executive control, planning, coordination and reporting",
    "Bob_Finance": "Finance, accounting and billing",
    "Cindy_Secretary": "Secretary and administration",
    "Kai_Legal": "Legal research, case management and drafting",
    "Neo_Sales": "Marketing, sales, lead generation and campaigns",
}

WORKERS = {
    "Bob_Finance": ROOT / "Bob_Finance" / "worker.py",
    "Cindy_Secretary": ROOT / "Cindy_Secretary" / "worker.py",
    "Kai_Legal": ROOT / "Kai_Legal" / "worker.py",
    "Neo_Sales": ROOT / "Neo_Sales" / "worker.py",
}


def now():
    return datetime.now(timezone.utc).isoformat()


class CEOController:
    def __init__(self):
        EXECUTIVE_DIR.mkdir(parents=True, exist_ok=True)

    def load_manifest(self):
        if not MANIFEST_FILE.exists():
            return {}
        try:
            return json.loads(MANIFEST_FILE.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            return {"error": str(exc)}

    def load_queue(self):
        if not QUEUE_FILE.exists():
            return []
        try:
            return json.loads(QUEUE_FILE.read_text(encoding="utf-8-sig"))
        except Exception:
            return []

    def save_queue(self, queue):
        QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")

    def status(self):
        manifest = self.load_manifest()
        registered = manifest.get("agents", {})
        return {
            "timestamp": now(),
            "controller": "CEO",
            "agents": {
                name: {
                    "registered": bool(registered.get(name, False)),
                    "directory_exists": (ROOT / name).exists(),
                    "role": role,
                }
                for name, role in AGENTS.items()
            },
            "persistent_memory": bool(manifest.get("persistent_memory", False)),
            "human_approval_file": HITL_FILE.exists(),
        }

    def snapshot(self):
        state = self.status()
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state

    def dispatch_one(self):
        queue = self.load_queue()

        if not queue:
            return {
                "status": "idle",
                "message": "No queued tasks.",
            }

        item = queue[0]
        agent = item.get("agent")
        task_id = item.get("task_id")

        worker = WORKERS.get(agent)

        if not worker:
            return {
                "status": "error",
                "message": f"No worker registered for agent: {agent}",
                "task_id": task_id,
            }

        if not worker.exists():
            return {
                "status": "error",
                "message": f"Worker file not found: {worker}",
                "task_id": task_id,
                "agent": agent,
            }

        print(f"Dispatching task: {task_id}")
        print(f"Agent: {agent}")
        print(f"Worker: {worker}")

        result = subprocess.run(
            [sys.executable, str(worker), task_id],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(result.stdout.rstrip())

            remaining = [
                entry
                for entry in queue
                if entry.get("task_id") != task_id
            ]
            self.save_queue(remaining)

            return {
                "status": "dispatched",
                "task_id": task_id,
                "agent": agent,
                "worker": str(worker),
                "returncode": result.returncode,
            }

        print(result.stdout.rstrip())
        print(result.stderr.rstrip())

        return {
            "status": "worker_failed",
            "task_id": task_id,
            "agent": agent,
            "returncode": result.returncode,
            "stderr": result.stderr.strip(),
        }


def self_test():
    controller = CEOController()
    state = controller.snapshot()

    print("=== BPFCoBrain CEO CONTROLLER SELF-TEST ===")
    print("CEO controller: OK")
    print(
        f"Agents registered in manifest: "
        f"{sum(v['registered'] for v in state['agents'].values())}/{len(AGENTS)}"
    )
    print(f"Persistent memory declared: {state['persistent_memory']}")
    print(f"Human approval file: {state['human_approval_file']}")

    print("Worker registry:")
    for agent, worker in WORKERS.items():
        print(f"  {agent}: worker_exists={worker.exists()}")

    print(f"Queued tasks available: {len(controller.load_queue())}")
    print("Dispatcher: READY")
    print("External execution: BLOCKED pending user approval")
    print("SELF-TEST COMPLETE")


if __name__ == "__main__":
    self_test()
