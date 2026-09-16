import json
from datetime import datetime, timezone
from pathlib import Path
from agent_bridge import AgentBridge

ROOT = Path(__file__).resolve().parent
EXECUTIVE_DIR = ROOT / "Brain" / "Executive"
PLAN_FILE = EXECUTIVE_DIR / "CEO_Work_Plan.md"
STATE_FILE = EXECUTIVE_DIR / "state.json"
QUEUE_FILE = EXECUTIVE_DIR / "queue.json"
REPORT_DIR = EXECUTIVE_DIR / "reports"

AGENT_PLANS = {
    "Bob_Finance": [
        "Review outstanding financial and billing items.",
        "Identify payments, invoices, or financial commitments requiring CEO attention.",
        "Prepare internal financial analysis; do not execute payments without approval.",
    ],
    "Cindy_Secretary": [
        "Review administrative, communication, and scheduling items.",
        "Identify messages or appointments requiring priority.",
        "Prepare drafts and coordination actions; do not send externally without approval.",
    ],
    "Kai_Legal": [
        "Review active legal/case-file items and deadlines.",
        "Identify legal risks, missing documents, or actions requiring escalation.",
        "Prepare internal legal drafts/research; do not file or serve without approval.",
    ],
    "Neo_Sales": [
        "Review active prospects, campaigns, and sales pipeline items.",
        "Identify high-value opportunities and follow-up priorities.",
        "Prepare internal outreach and campaign material; do not send or publish without approval.",
    ],
}


def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def run():
    EXECUTIVE_DIR.mkdir(parents=True, exist_ok=True)

    state = load_json(STATE_FILE, {})
    queue = load_json(QUEUE_FILE, [])

    # CEO dispatches internal work only when the same objective is not
    # already queued, in progress, or recently completed.
    bridge = AgentBridge()

    active_objectives = set()
    for item in queue:
        task_id = item.get("task_id")
        task_path = EXECUTIVE_DIR / "tasks" / f"{task_id}.json"
        task = load_json(task_path, {})
        if task.get("objective"):
            active_objectives.add(
                (task.get("agent"), task.get("objective"))
            )

    completed_objectives = set()
    for path in (EXECUTIVE_DIR / "tasks").glob("*.json"):
        task = load_json(path, {})
        if task.get("status") == "complete":
            completed_objectives.add(
                (task.get("agent"), task.get("objective"))
            )

    for agent, actions in AGENT_PLANS.items():
        for action in actions[:1]:
            key = (agent, action)
            if key in active_objectives or key in completed_objectives:
                continue

            bridge.dispatch(
                agent,
                action,
                priority="normal",
                approval_required=True,
            )

    queue = load_json(QUEUE_FILE, [])

    reports = []
    for path in sorted(REPORT_DIR.glob("*.json")):
        data = load_json(path, {})
        if data:
            reports.append(data)

    lines = [
        "# CEO Work Plan",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Executive Direction",
        "",
        "The CEO coordinates the specialist agents, prioritizes internal work, "
        "reviews their reports, and escalates external or high-impact actions "
        "for user approval.",
        "",
        "## Immediate Specialist Priorities",
        "",
    ]

    for agent, actions in AGENT_PLANS.items():
        status = state.get("agents", {}).get(agent, {})
        lines.append(f"### {agent}")
        lines.append(
            f"Role status: registered={status.get('registered', False)}; "
            f"directory={status.get('directory_exists', False)}"
        )
        for action in actions:
            lines.append(f"- {action}")
        lines.append("")

    lines += ["## Existing Work", ""]

    if queue:
        for item in queue:
            lines.append(
                f"- Queued: **{item.get('agent', 'Unknown')}** — "
                f"`{item.get('task_id', '')}` ({item.get('status', '')})"
            )
    else:
        lines.append("- No queued CEO tasks.")

    if reports:
        lines += ["", "Recent reports:"]
        for report in reports[-10:]:
            summary = str(report.get("summary", "")).replace("\n", " ")
            lines.append(
                f"- **{report.get('agent', 'Unknown')}** — "
                f"{report.get('status', 'unknown')}: {summary}"
            )
    else:
        lines.append("- No agent reports available.")

    lines += [
        "",
        "## Planning Rule",
        "",
        "- Research, analysis, drafting, indexing, organization, and internal coordination may proceed.",
        "- External sends, payments, publications, legal filings, contracts, and other high-impact execution require explicit user approval.",
        "- Planning is advisory until a real agent claims the task through the bridge.",
        "",
    ]

    PLAN_FILE.write_text("\n".join(lines), encoding="utf-8")

    print("=== BPFCoBrain CEO PLANNER SELF-TEST ===")
    print("CEO work plan: OK")
    print(f"Specialist plans: {len(AGENT_PLANS)}")
    print(f"Queued tasks considered: {len(queue)}")
    print(f"Reports considered: {len(reports)}")
    print(f"Plan: {PLAN_FILE}")
    print("External execution: BLOCKED pending user approval")
    print("PLANNER SELF-TEST COMPLETE")


if __name__ == "__main__":
    run()
