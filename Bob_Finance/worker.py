from pathlib import Path
import sys

# Make the BPFCoBrain root available when this worker is
# launched directly from the Bob_Finance directory.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import json

from agent_bridge import AgentBridge

AGENT = "Bob_Finance"
BRAIN_ROOT = REPO_ROOT / "Brain"
EXECUTIVE_ROOT = BRAIN_ROOT / "Executive"


from runtime_adapter import lifecycle

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def inspect_finance_sources():
    findings = []
    finance_extensions = {".json", ".md", ".txt", ".csv"}

    for path in BRAIN_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in finance_extensions:
            continue

        if EXECUTIVE_ROOT in path.parents or path.parent == EXECUTIVE_ROOT:
            continue

        name = path.name.lower()

        finance_terms = (
            "finance",
            "financial",
            "invoice",
            "billing",
            "payment",
            "account",
            "accounts",
            "expense",
            "income",
            "cashflow",
            "cash_flow",
        )

        if any(term in name for term in finance_terms):
            findings.append({
                "file": str(path),
                "size": path.stat().st_size,
            })

    return findings


def build_finance_review(task):
    state = load_json(EXECUTIVE_ROOT / "state.json")
    finance_sources = inspect_finance_sources()

    registered = state.get("agents", {}).get(AGENT, {})

    if finance_sources:
        source_lines = [
            f"- {item['file']} ({item['size']} bytes)"
            for item in finance_sources
        ]
        evidence_status = "Finance-related source files detected."
    else:
        source_lines = [
            "- No finance, billing, invoice, payment, account, or expense "
            "source files were found in the Brain outside the Executive control layer."
        ]
        evidence_status = "No finance source data is currently available."

    review = [
        "BOB FINANCE INTERNAL REVIEW",
        "",
        f"Task: {task.get('objective', 'No objective supplied.')}",
        f"Agent registration: {registered.get('registered', False)}",
        f"Evidence status: {evidence_status}",
        "",
        "Finance evidence:",
        *source_lines,
        "",
        "Assessment:",
        "No financial figures, invoices, payments, balances, or commitments "
        "were inferred because the Brain currently contains no verified finance "
        "source data outside the Executive control layer.",
        "",
        "Required next input:",
        "Finance source documents or structured finance data can be indexed into "
        "the Brain before Bob performs substantive financial analysis.",
        "",
        "External execution:",
        "BLOCKED pending user approval.",
    ]

    return "\n".join(review)


def run(task_id):
    def processor(task):
        return build_finance_review(task)

    result = lifecycle(task_id, processor)
    report = result.get("report", {})

    print(f"{AGENT} WORKER COMPLETE")
    print(f"Task: {task_id}")
    print(f"Report: {report.get('task_id', task_id)}")
    print("Returned to CEO: YES")
    print("Finance evidence fabricated: NO")
    print("External execution: BLOCKED pending user approval")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python worker.py <task_id>")

    run(sys.argv[1])

