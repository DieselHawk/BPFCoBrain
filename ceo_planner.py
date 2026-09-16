import json
from datetime import datetime, timezone
from pathlib import Path
from agent_bridge import AgentBridge

ROOT = Path(__file__).resolve().parent
EXECUTIVE_DIR = ROOT / "Brain" / "Executive"
PLAN_FILE = EXECUTIVE_DIR / "CEO_Work_Plan.md"
STATE_FILE = EXECUTIVE_DIR / "state.json"
QUEUE_FILE = EXECUTIVE_DIR / "queue.json"
TASK_DIR = EXECUTIVE_DIR / "tasks"
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


def collect_reports():
    reports = []
    for path in sorted(REPORT_DIR.glob("*.json")):
        data = load_json(path, {})
        if data:
            reports.append(data)
    return reports


def collect_completed_objectives():
    completed = set()
    for path in TASK_DIR.glob("*.json"):
        task = load_json(path, {})
        if task.get("status") == "complete":
            completed.add((task.get("agent"), task.get("objective")))
    return completed


def collect_active_objectives(queue):
    # Treat the task records as the source of truth.
    # queue.json can become stale or be repaired independently.
    active = set()

    for path in TASK_DIR.glob("*.json"):
        task = load_json(path, {})
        if task.get("status") in {"queued", "in_progress"}:
            if task.get("agent") and task.get("objective"):
                active.add((task.get("agent"), task.get("objective")))

    return active


def build_report_assessment(reports):
    assessment = []

    for report in reports[-10:]:
        agent = report.get("agent", "Unknown")
        status = report.get("status", "unknown")
        summary = " ".join(str(report.get("summary", "")).split())

        if status in {"complete", "completed"}:
            assessment.append(
                f"- {agent}: completed — {summary or 'No summary supplied.'}"
            )
        else:
            assessment.append(
                f"- {agent}: requires attention — {summary or 'No summary supplied.'}"
            )

    return assessment


def run():
    EXECUTIVE_DIR.mkdir(parents=True, exist_ok=True)

    state = load_json(STATE_FILE, {})
    queue = load_json(QUEUE_FILE, [])
    reports = collect_reports()

    bridge = AgentBridge()

    active_objectives = collect_active_objectives(queue)
    completed_objectives = collect_completed_objectives()

    dispatched = []

    for agent, actions in AGENT_PLANS.items():
        # CEO advances an agent one step at a time.
        # The next objective is only dispatched when the previous
        # objective has been completed and no later objective is active.
        for index, action in enumerate(actions):
            key = (agent, action)

            if key in active_objectives:
                break

            if key in completed_objectives:
                continue

            # Do not skip ahead. The first incomplete objective is
            # the only objective the CEO may dispatch for this agent.
            if index > 0:
                previous_key = (agent, actions[index - 1])
                if previous_key not in completed_objectives:
                    break

            bridge.dispatch(
                agent,
                action,
                priority="normal",
                approval_required=True,
            )
            dispatched.append((agent, action))
            break

    queue = load_json(QUEUE_FILE, [])

    lines = [
        "# CEO Work Plan",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Executive Direction",
        "",
        "The CEO coordinates the specialist agents, reviews returned reports, "
        "prioritizes internal work, and escalates external or high-impact actions "
        "for user approval.",
        "",
        "## Executive Assessment",
        "",
    ]

    assessment = build_report_assessment(reports)

    if assessment:
        lines.extend(assessment)
    else:
        lines.append("- No agent reports available for assessment.")

    lines.extend([
        "",
        "## Immediate Specialist Priorities",
        "",
    ])

    for agent, actions in AGENT_PLANS.items():
        status = state.get("agents", {}).get(agent, {})
        lines.append(f"### {agent}")
        lines.append(
            f"Role status: registered={status.get('registered', False)}; "
            f"directory={status.get('directory_exists', False)}"
        )

        key = (agent, actions[0])
        if key in completed_objectives:
            lines.append(f"- COMPLETED: {actions[0]}")
        elif key in active_objectives:
            lines.append(f"- ACTIVE/QUEUED: {actions[0]}")
        else:
            lines.append(f"- DISPATCHED: {actions[0]}")

        for action in actions[1:]:
            lines.append(f"- {action}")

        lines.append("")

    lines += ["## Current CEO Queue", ""]

    if queue:
        for item in queue:
            lines.append(
                f"- **{item.get('agent', 'Unknown')}** — "
                f"`{item.get('task_id', '')}` ({item.get('status', '')})"
            )
    else:
        lines.append("- No queued CEO tasks.")

    lines += [
        "",
        "## Agent Reports",
        "",
    ]

    if reports:
        for report in reports[-10:]:
            summary = " ".join(str(report.get("summary", "")).split())
            lines.append(
                f"- **{report.get('agent', 'Unknown')}** — "
                f"{report.get('status', 'unknown')}: "
                f"{summary or 'No summary supplied.'}"
            )
    else:
        lines.append("- No agent reports available.")

    lines += [
        "",
        "## CEO Planning Rules",
        "",
        "- Completed objectives are not re-dispatched.",
        "- Active or queued objectives are not duplicated.",
        "- Research, analysis, drafting, indexing, organization, and internal coordination may proceed.",
        "- External sends, payments, publications, legal filings, contracts, and other high-impact execution require explicit user approval.",
        "- External execution remains blocked pending user approval.",
        "",
        "## Execution Status",
        "",
        f"- New tasks dispatched this cycle: {len(dispatched)}",
        f"- Reports assessed this cycle: {len(reports)}",
        f"- Current queued tasks: {len(queue)}",
        "",
    ]

    PLAN_FILE.write_text("\n".join(lines), encoding="utf-8")

    print("=== BPFCoBrain CEO PLANNER SELF-TEST ===")
    print("CEO work plan: OK")
    print(f"Specialist plans: {len(AGENT_PLANS)}")
    print(f"Reports assessed: {len(reports)}")
    print(f"New tasks dispatched: {len(dispatched)}")
    print(f"Current queued tasks: {len(queue)}")
    print(f"Plan: {PLAN_FILE}")
    print("External execution: BLOCKED pending user approval")
    print("PLANNER SELF-TEST COMPLETE")


if __name__ == "__main__":
    run()
