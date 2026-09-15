import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXECUTIVE_DIR = ROOT / "Brain" / "Executive"
STATE_FILE = EXECUTIVE_DIR / "state.json"
MANIFEST_FILE = ROOT / "Shared_Context" / "manifest.json"
HITL_FILE = ROOT / "Human_In_The_Loop.md"

AGENTS = {
    "CEO": "Executive control, planning, coordination and reporting",
    "Bob_Finance": "Finance, accounting and billing",
    "Cindy_Secretary": "Secretary and administration",
    "Kai_Legal": "Legal research, case management and drafting",
    "Neo_Sales": "Marketing, sales, lead generation and campaigns",
}

class CEOController:
    def __init__(self):
        EXECUTIVE_DIR.mkdir(parents=True, exist_ok=True)

    def load_manifest(self):
        if not MANIFEST_FILE.exists():
            return {}
        try:
            return json.loads(MANIFEST_FILE.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            return {"error": str(exc)}

    def status(self):
        manifest = self.load_manifest()
        registered = manifest.get("agents", {})
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "controller": "CEO",
            "agents": {
                name: {
                    "registered": bool(registered.get(name, False)),
                    "directory_exists": (ROOT / name).exists(),
                    "role": role,
                }
                for name, role in AGENTS.items()
            },
            "persistent_memory": bool(manifest.get("persistent_memory", False)),
            "human_approval_file": HITL_FILE.exists(),
        }

    def snapshot(self):
        state = self.status()
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state

def self_test():
    controller = CEOController()
    state = controller.snapshot()

    print("=== BPFCoBrain CEO CONTROLLER SELF-TEST ===")
    print("CEO controller: OK")
    print(f"Agents registered in manifest: {sum(v['registered'] for v in state['agents'].values())}/{len(AGENTS)}")
    print(f"Persistent memory declared: {state['persistent_memory']}")
    print(f"Human approval file: {state['human_approval_file']}")
    print("Agent registry:")
    for name, details in state["agents"].items():
        print(f"  {name}: registered={details['registered']}, directory={details['directory_exists']}")
    print("SELF-TEST COMPLETE")

if __name__ == "__main__":
    self_test()
