from pathlib import Path
import subprocess
from approval_gate import request, is_approved

REPO_ROOT = Path(__file__).resolve().parent.parent


def prepare_git(action, args=None):
    record = request(
        action=f"git.{action}",
        agent="Cindy_Secretary",
        payload={
            "repository": str(REPO_ROOT),
            "args": args or [],
        },
    )

    print("CINDY GIT ACTION PREPARED")
    print(f"Approval ID: {record['approval_id']}")
    print(f"Action: git.{action}")
    print("Status: PENDING HUMAN APPROVAL")
    print("External execution: BLOCKED")

    return record


def execute_approved_git(approval_id):
    if not is_approved(approval_id):
        raise PermissionError(
            "Human approval required. Git execution is BLOCKED."
        )

    approval_file = (
        REPO_ROOT / "Brain" / "Executive" /
        "Approvals" / "Approved" / f"{approval_id}.json"
    )

    import json
    record = json.loads(
        approval_file.read_text(encoding="utf-8")
    )

    payload = record["payload"]
    args = payload.get("args", [])

    allowed = {
        "status",
        "diff",
        "log",
        "branch",
        "show",
        "add",
        "commit",
        "push",
        "pull",
    }

    if not args or args[0] not in allowed:
        raise PermissionError(
            f"Git operation not permitted: {args}"
        )

    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    print("CINDY GIT EXECUTION COMPLETE")
    print(f"Approval ID: {approval_id}")
    print(f"Return code: {result.returncode}")

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return result.returncode


if __name__ == "__main__":
    print("Cindy Git approval module loaded.")

