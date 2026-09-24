"""Verify the shared context in the checkout being launched."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ("CEO", "Bob_Finance", "Cindy_Secretary", "Kai_Legal", "Neo_Sales")

def verify_and_sync():
    shared = ROOT / "Shared_Context"
    shared.mkdir(parents=True, exist_ok=True)
    status = {agent: (ROOT / agent).is_dir() for agent in AGENTS}
    manifest = {
        "agents": status,
        "persistent_memory": (ROOT / "Human_In_The_Loop.md").exists(),
        "vault_path": str(ROOT),
        "shared_experience_path": str(ROOT / "Brain" / "Executive" / "Experience"),
    }
    target = shared / "manifest.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    temporary.replace(target)
    print(f"[BPFCoBrain] Vault context verified: {ROOT}")

if __name__ == "__main__":
    verify_and_sync()
