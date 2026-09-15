import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHARED_DIR = ROOT / "Shared_Context"
EXECUTIVE_DIR = ROOT / "Brain" / "Executive"
SNAPSHOT_FILE = EXECUTIVE_DIR / "shared_context.json"
MANIFEST_FILE = SHARED_DIR / "manifest.json"

AGENTS = [
    "CEO",
    "Bob_Finance",
    "Cindy_Secretary",
    "Kai_Legal",
    "Neo_Sales",
]

ALLOWED_EXTENSIONS = {".md", ".json", ".txt", ".yaml", ".yml"}


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc)}


def collect_files(folder):
    files = []

    if not folder.exists():
        return files

    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        try:
            size = path.stat().st_size
            files.append({
                "name": path.name,
                "path": str(path.relative_to(ROOT)),
                "size": size,
            })
        except OSError:
            pass

    return files


class SharedContextBridge:
    def __init__(self):
        EXECUTIVE_DIR.mkdir(parents=True, exist_ok=True)

    def snapshot(self):
        manifest = read_json(MANIFEST_FILE) if MANIFEST_FILE.exists() else {}

        agents = {}
        for agent in AGENTS:
            agents[agent] = {
                "registered": bool(manifest.get("agents", {}).get(agent, False)),
                "workspace": str((ROOT / agent).relative_to(ROOT)),
                "files": collect_files(ROOT / agent),
            }

        shared_files = collect_files(SHARED_DIR)

        snapshot = {
            "generated_at": now(),
            "source_of_truth": "C:\\BPFCo\\BPFCoBrain",
            "persistent_memory_declared": bool(manifest.get("persistent_memory", False)),
            "agents": agents,
            "shared_context_files": shared_files,
            "human_approval_file": {
                "path": "Human_In_The_Loop.md",
                "exists": (ROOT / "Human_In_The_Loop.md").exists(),
            },
        }

        SNAPSHOT_FILE.write_text(
            json.dumps(snapshot, indent=2),
            encoding="utf-8",
        )

        return snapshot


def self_test():
    bridge = SharedContextBridge()
    snapshot = bridge.snapshot()

    print("=== BPFCoBrain SHARED CONTEXT BRIDGE SELF-TEST ===")
    print("Shared context snapshot: OK")
    print(f"Agents discovered: {len(snapshot['agents'])}")
    print(f"Persistent memory declared: {snapshot['persistent_memory_declared']}")
    print(f"Human approval file: {snapshot['human_approval_file']['exists']}")

    for name, details in snapshot["agents"].items():
        print(
            f"  {name}: registered={details['registered']}, "
            f"files={len(details['files'])}"
        )

    print(f"Snapshot: {SNAPSHOT_FILE}")
    print("SELF-TEST COMPLETE")


if __name__ == "__main__":
    self_test()
