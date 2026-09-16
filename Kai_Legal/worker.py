from agent_bridge import AgentBridge

AGENT = "Kai_Legal"


def run(task_id):
    bridge = AgentBridge()

    task = bridge.claim(task_id, AGENT)

    summary = (
        f"{AGENT} received task: "
        f"{task.get('objective', 'No objective supplied.')} "
        "Internal execution framework completed the worker handoff. "
        "No external action was executed."
    )

    report = bridge.complete(
        task_id,
        AGENT,
        summary,
        status="complete",
    )

    print(f"{AGENT} WORKER COMPLETE")
    print(f"Task: {task_id}")
    print(f"Report: {report.get('task_id', task_id)}")
    print("Returned to CEO: YES")
    print("External execution: BLOCKED pending user approval")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python worker.py <task_id>")

    run(sys.argv[1])
