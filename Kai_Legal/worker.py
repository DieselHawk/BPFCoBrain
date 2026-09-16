from pathlib import Path
import sys
import json
import re

# Make the BPFCoBrain root available when launched directly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_bridge import AgentBridge

AGENT = "Kai_Legal"
BRAIN_ROOT = REPO_ROOT / "Brain"
EXECUTIVE_ROOT = BRAIN_ROOT / "Executive"

SOURCE_EXTENSIONS = {".json", ".md", ".txt", ".csv"}

LEGAL_TERMS = (
    "court",
    "case",
    "legal",
    "affidavit",
    "trust",
    "trustee",
    "deed",
    "subpoena",
    "paia",
    "motion",
    "notice",
    "order",
    "judgment",
    "summons",
    "pleading",
    "litigation",
    "attorney",
    "law",
    "deadline",
    "hearing",
    "application",
)


from runtime_adapter import lifecycle

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def inspect_legal_sources():
    findings = []

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue

        if ".git" in path.parts or "__pycache__" in path.parts:
            continue

        # Executive files are control/state records, not case evidence.
        if EXECUTIVE_ROOT in path.parents:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        haystack = (path.name + "\n" + text).lower()

        matches = sorted({
            term for term in LEGAL_TERMS
            if re.search(r"\b" + re.escape(term) + r"\b", haystack)
        })

        if matches:
            findings.append({
                "file": str(path),
                "size": path.stat().st_size,
                "indicators": matches,
            })

    return findings


def build_legal_review(task):
    sources = inspect_legal_sources()

    if sources:
        source_lines = []
        for item in sources:
            indicators = ", ".join(item["indicators"])
            source_lines.append(
                f"- {item['file']} ({item['size']} bytes; indicators: {indicators})"
            )

        evidence_status = (
            "Potential legal/case-related source files detected by content indicators."
        )
    else:
        source_lines = [
            "- No verified legal or case-related source files were detected."
        ]

        evidence_status = (
            "No legal/case source data is currently available."
        )

    review = [
        "KAI LEGAL INTERNAL REVIEW",
        "",
        f"Task: {task.get('objective', 'No objective supplied.')}",
        f"Evidence status: {evidence_status}",
        "",
        "Potential legal/case sources:",
        *source_lines,
        "",
        "Deadline assessment:",
        "No legal deadline, hearing date, filing date, or procedural requirement "
        "was inferred unless supported by verified source material.",
        "",
        "Risk / missing-information assessment:",
        "The current Brain does not establish a complete legal case record. "
        "Any detected files require substantive review before legal conclusions "
        "or deadline decisions are made.",
        "",
        "Required next input:",
        "Relevant case documents can be indexed into the Brain so Kai can perform "
        "document-grounded case review, deadline extraction, and internal drafting.",
        "",
        "External execution:",
        "BLOCKED pending user approval.",
    ]

    return "\n".join(review)


def run(task_id):
    def processor(task):
        return build_legal_review(task)

    result = lifecycle(task_id, processor)
    report = result.get("report", {})

    print(f"{AGENT} WORKER COMPLETE")
    print(f"Task: {task_id}")
    print(f"Report: {report.get('task_id', task_id)}")
    print("Returned to CEO: YES")
    print("Legal conclusions fabricated: NO")
    print("External execution: BLOCKED pending user approval")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python worker.py <task_id>")

    run(sys.argv[1])

