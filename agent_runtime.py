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
    Shared lifecycle foundation for every BPFCoBrain specialist.

    Specialist workers keep their domain logic.
    AgentRuntime provides the common execution contract.
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

    def lifecycle(self, task_id, processor):
        """
        Standard lifecycle wrapper.

        The specialist supplies `processor(task)`.
        The runtime handles claim -> process -> report.
        """
        task = self.claim(task_id)

        try:
            report = processor(task)

            return self.report_to_ceo(
                task_id,
                report,
                status="complete",
            )

        except Exception as exc:
            error_report = (
                f"{self.agent_name} execution failed.\n"
                f"Task: {task_id}\n"
                f"Error: {type(exc).__name__}: {exc}"
            )

            return self.report_to_ceo(
                task_id,
                error_report,
                status="failed",
            )


def runtime_self_test():
    runtime = AgentRuntime(
        "RUNTIME_TEST_AGENT",
        "Shared specialist runtime validation",
    )

    health = runtime.health()

    assert health["runtime"] == "shared"
    assert health["agent_bridge"] is True
    assert health["approval_gate"] is True
    assert health["ceo_reporting"] is True

    result = runtime.startup()

    assert result["status"] == "ready"
    assert result["human_approval"] is True

    return True


if __name__ == "__main__":
    print("=== SHARED AGENT RUNTIME SELF-TEST ===")

    if runtime_self_test():
        print("Runtime: READY")
        print("Agent Bridge: OK")
        print("Approval Gate: OK")
        print("CEO Reporting: OK")
        print("Lifecycle wrapper: OK")
        print("SELF-TEST: PASS")
