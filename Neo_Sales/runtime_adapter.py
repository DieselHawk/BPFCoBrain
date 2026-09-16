from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_runtime import AgentRuntime

AGENT = "Neo_Sales"
ROLE = "Marketing, sales, lead generation and campaigns"

runtime = AgentRuntime(
    agent_name=AGENT,
    role=ROLE,
)

def startup():
    return runtime.startup()

def claim(task_id):
    return runtime.claim(task_id)

def complete(task_id, report, status="complete"):
    return runtime.complete(task_id, report, status)

def report_to_ceo(task_id, report, status="complete"):
    return runtime.report_to_ceo(task_id, report, status)

def health():
    return runtime.health()

def lifecycle(task_id, processor):
    return runtime.lifecycle(task_id, processor)
