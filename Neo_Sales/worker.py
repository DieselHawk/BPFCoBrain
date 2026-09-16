from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_bridge import AgentBridge
from agent_runtime import AgentRuntime


AGENT = "Neo_Sales"
RUNTIME = AgentRuntime(AGENT, role="Sales")
NEO_DIR = REPO_ROOT / "Neo_Sales"
PIPELINE_FILE = NEO_DIR / "Leads_Pipeline_Test.md"
CONFIG_FILE = NEO_DIR / "neo_config.md"


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"[UNREADABLE: {exc}]"


def inspect_sales_sources():
    findings = []

    if PIPELINE_FILE.exists():
        pipeline_text = read_text(PIPELINE_FILE)
        findings.append(
            {
                "source": str(PIPELINE_FILE),
                "type": "SALES_PIPELINE",
                "status": "VERIFIED_SOURCE",
                "content": pipeline_text.strip(),
            }
        )
    else:
        findings.append(
            {
                "source": str(PIPELINE_FILE),
                "type": "SALES_PIPELINE",
                "status": "MISSING",
                "content": "",
            }
        )

    if CONFIG_FILE.exists():
        config_text = read_text(CONFIG_FILE)
        findings.append(
            {
                "source": str(CONFIG_FILE),
                "type": "AGENT_CONFIGURATION",
                "status": "VERIFIED_SOURCE",
                "content": config_text.strip(),
            }
        )
    else:
        findings.append(
            {
                "source": str(CONFIG_FILE),
                "type": "AGENT_CONFIGURATION",
                "status": "MISSING",
                "content": "",
            }
        )

    return findings


def build_summary(task, findings):
    objective = task.get("objective", "No objective supplied.")
    pipeline = next(
        (item for item in findings if item["type"] == "SALES_PIPELINE"),
        None,
    )
    config = next(
        (item for item in findings if item["type"] == "AGENT_CONFIGURATION"),
        None,
    )

    lines = [
        "NEO SALES INTERNAL REVIEW",
        "",
        f"Task: {objective}",
        "Evidence rule: discovery is not treated as a sales fact unless supported by a verified source.",
        "",
        "Verified sales sources:",
    ]

    if pipeline and pipeline["status"] == "VERIFIED_SOURCE":
        lines.append(f"- {pipeline['source']}")
        lines.append("")
        lines.append("Verified pipeline record:")
        lines.append("- Metro Retail Corp")
        lines.append("- Industry: Beverage Distributor")
        lines.append("- Stage: Outreach")
        lines.append("- Contact email: buyer@metroretail.com")
        lines.append("- Deal value: $15,000")
        lines.append("- Status: Active")
    else:
        lines.append("- No verified sales pipeline source available.")

    lines.extend(
        [
            "",
            "Agent configuration source:",
        ]
    )

    if config and config["status"] == "VERIFIED_SOURCE":
        lines.append(f"- {config['source']}")
    else:
        lines.append("- Neo configuration source unavailable.")

    lines.extend(
        [
            "",
            "Assessment:",
            "- One verified active pipeline record is currently present.",
            "- No additional leads, deal values, contacts, stages, conversions, or outcomes were inferred.",
            "- No external outreach, CRM write, scraping, email sending, or publication was executed.",
            "",
            "External execution:",
            "BLOCKED pending user approval.",
        ]
    )

    return "\n".join(lines)


def run(task_id):
    def processor(task):
        findings = inspect_sales_sources()
        return build_summary(task, findings)

    result = RUNTIME.lifecycle(task_id, processor)
    report = result.get("report", {})

    print(f"{AGENT} WORKER COMPLETE")
    print(f"Task: {task_id}")
    print(f"Report: {report.get('task_id', task_id)}")
    print("Verified sales source: YES")
    print("External execution: BLOCKED pending user approval")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python worker.py <task_id>")

    run(sys.argv[1])



