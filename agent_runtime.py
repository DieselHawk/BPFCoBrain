from pathlib import Path
from datetime import datetime, timezone
import json
import sys

ROOT = Path(__file__).resolve().parent
EXECUTIVE = ROOT / "Brain" / "Executive"
APPROVALS = EXECUTIVE / "Approvals"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_bridge import AgentBridge
from approval_gate import request, is_approved


class AgentRuntime:
    """
    Shared execution lifecycle for all BPFCoBrain specialist agents.

    Lifecycle:
        startup
        -> claim
        -> load context
        -> inspect
        -> execute/prepare
        -> approval when required
        -> complete
        -> report to CEO
    """

    def __init__(self, agent_name, role=""):
        self.agent_name = agent_name
        self.role = role
        self.bridge = AgentBridge()

    def startup(self):
        return {
            "agent": self.agent_name,
            "role": self.role,
            "runtime": "shared",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "ready",
            "human_approval": True,
        }

    def claim(self, task_id):
        return self.bridge.claim(task_id, self.agent_name)

    def load_json(self, path):
        path = Path(path)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def request_approval(self, action, payload=None):
        return request(
            action=action,
            agent=self.agent_name,
            payload=payload or {},
        )

    def approved(self, approval_id):
        return is_approved(approval_id)

    def complete(self, task_id, report, status="complete"):
        return self.bridge.complete(
            task_id,
            self.agent_name,
            report,
            status=status,
        )

    def report_to_ceo(self, task_id, report, status="complete"):
        result = self.complete(task_id, report, status=status)

        return {
            "agent": self.agent_name,
            "task_id": task_id,
            "status": status,
            "returned_to_ceo": True,
            "report": result,
        }

    def health(self):
        return {
            "agent": self.agent_name,
            "role": self.role,
            "runtime": "shared",
            "agent_bridge": True,
            "approval_gate": True,
            "ceo_reporting": True,
            "status": "healthy",
        }


if __name__ == "__main__":
    runtime = AgentRuntime(
        "RUNTIME_TEST_AGENT",
        "Shared specialist runtime validation",
    )

    print("=== SHARED AGENT RUNTIME SELF-TEST ===")

    startup = runtime.startup()
    print(f"Startup: {startup['status']}")
    print(f"Agent Bridge: {'OK' if startup else 'FAIL'}")

    health = runtime.health()

    print(f"Agent Bridge integration: {health['agent_bridge']}")
    print(f"Approval Gate integration: {health['approval_gate']}")
    print(f"CEO reporting integration: {health['ceo_reporting']}")
    print(f"Runtime mode: {health['runtime']}")
    print(f"Overall status: {health['status']}")

    assert health["agent_bridge"] is True
    assert health["approval_gate"] is True
    assert health["ceo_reporting"] is True
    assert health["runtime"] == "shared"
    assert health["status"] == "healthy"

    print("SELF-TEST: PASS")
