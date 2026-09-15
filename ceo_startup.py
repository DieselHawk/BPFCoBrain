import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXECUTIVE_DIR = ROOT / "Brain" / "Executive"
STATE_FILE = EXECUTIVE_DIR / "state.json"
CONTEXT_FILE = EXECUTIVE_DIR / "shared_context.json"
QUEUE_FILE = EXECUTIVE_DIR / "queue.json"
TASK_DIR = EXECUTIVE_DIR / "tasks"
REPORT_DIR = EXECUTIVE_DIR / "reports"
STARTUP_REPORT = EXECUTIVE_DIR / "CEO_Morning_Report.md"

AGENTS = {
    "Bob_Finance": "Finance, accounting and billing",
    "Cindy_Secretary": "Secretary and administration",
    "Kai_Legal": "Legal research, case management and drafting",
    "Neo_Sales": "Marketing, sales, lead generation and campaigns",
}


def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def get_reports():
    reports = []
    for path in sorted(REPORT_DIR.glob("*.json")):
        data = load_json(path, {})
        if data:
            reports.append(data)
    return reports


def get_tasks():
    tasks = []
    for path in sorted(TASK_DIR.glob("*.json")):
        data = load_json(path, {})
        if data:
            tasks.append(data)
    return tasks


class CEOStartup:
    def run(self):
        EXECUTIVE_DIR.mkdir(parents=True, exist_ok=True)

        state = load_json(STATE_FILE, {})
        context = load_json(CONTEXT_FILE, {})
        queue = load_json(QUEUE_FILE, [])
        tasks = get_tasks()
        reports = get_reports()

        queued_count = len(queue)
        active_tasks = sum(1 for t in tasks if t.get("status") == "in_progress")
        completed_reports = sum(1 for r in reports if r.get("status") == "complete")

        attention = []

        for agent in AGENTS:
            details = state.get("agents", {}).get(agent, {})
            if not details.get("registered", False):
                attention.append(f"{agent} is not registered in the manifest.")

        for item in queue:
            attention.append(
                f"Queued task for {item.get('agent', 'unknown')}: {item.get('task_id', 'unknown')}"
            )

        for report in reports:
            if report.get("status") not in {"complete", "completed"}:
                attention.append(
                    f"Report requiring attention from {report.get('agent', 'unknown')}: "
                    f"{report.get('task_id', 'unknown')}"
                )

        lines = [
            "# CEO Morning Executive Report",
            "",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Executive Status",
            "",
            f"- Registered specialist agents: {len(AGENTS)}",
            f"- Queued tasks: {queued_count}",
            f"- Tasks in progress: {active_tasks}",
            f"- Returned completed reports: {completed_reports}",
            f"- Persistent memory declared: {state.get('persistent_memory', False)}",
            f"- Human approval gate present: {state.get('human_approval_file', False)}",
            "",
            "## Agent Roster",
            "",
        ]

        for agent, role in AGENTS.items():
            details = state.get("agents", {}).get(agent, {})
            lines.append(
                f"- **{agent}** — {role} "
                f"(registered={details.get('registered', False)}, "
                f"workspace_files={len(context.get('agents', {}).get(agent, {}).get('files', []))})"
            )

        lines.extend([
            "",
            "## Current Queue",
            "",
        ])

        if queue:
            for item in queue:
                lines.append(
                    f"- `{item.get('task_id', '')}` → **{item.get('agent', '')}** "
                    f"({item.get('status', '')})"
                )
        else:
            lines.append("- No queued tasks.")

        lines.extend([
            "",
            "## Recent Agent Reports",
            "",
        ])

        if reports:
            for report in reports[-10:]:
                summary = str(report.get("summary", "")).replace("\n", " ")
                lines.append(
                    f"- **{report.get('agent', 'Unknown')}** — "
                    f"{report.get('status', 'unknown')}: {summary}"
                )
        else:
            lines.append("- No reports yet.")

        lines.extend([
            "",
            "## CEO Attention / Planning",
            "",
        ])

        if attention:
            for item in attention:
                lines.append(f"- {item}")
        else:
            lines.append("- No immediate exceptions detected.")

        lines.extend([
            "",
            "## Execution Rule",
            "",
            "Internal research, analysis, drafting, indexing and coordination may proceed.",
            "External sends, publications, payments, legal filings, contractual commitments "
            "and other high-impact external execution remain blocked pending user approval.",
            "",
        ])

        STARTUP_REPORT.write_text("\n".join(lines), encoding="utf-8")

        print("=== BPFCoBrain CEO STARTUP SELF-TEST ===")
        print("CEO startup scan: OK")
        print(f"Agents: {len(AGENTS)}")
        print(f"Queued tasks: {queued_count}")
        print(f"Active tasks: {active_tasks}")
        print(f"Agent reports: {completed_reports}")
        print(f"Planning report: {STARTUP_REPORT}")
        print("External execution: BLOCKED pending user approval")
        print("STARTUP SELF-TEST COMPLETE")


if __name__ == "__main__":
    CEOStartup().run()
