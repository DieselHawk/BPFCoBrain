from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "Brain" / "Executive" / "LinkRepair" / "link_repair_report.json"

def apply_fix(source_path, old_text, new_text):
    """Replace a broken link with a working one in a file."""
    if not source_path.exists():
        return False
    
    content = source_path.read_text(encoding="utf-8")
    # We use a regex or exact replacement. 
    # Since links are often [[link]], we try to target the exact string.
    if old_text in content:
        new_content = content.replace(old_text, new_text)
        source_path.write_text(new_content, encoding="utf-8")
        return True
    return False

def main():
    if not REPORT.exists():
        print(f"❌ No report found at {REPORT}. Run the compiler first.")
        return

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    proposals = report.get("proposals", {})
    high = proposals.get("high_confidence", [])

    print(f"=== BPFCo LINK REPAIR APPLIER ===")
    print(f"Found {len(high)} high-confidence fixes to apply.\n")

    fixed_count = 0
    for item in high:
        source_key = item["source"]
        target_broken = item["target"]
        
        # Find the actual file path for the source
        # We need to look it up in the vault index or assume it's in the vault
        # For safety, we'll search the vault for the source_key .md file
        source_file = None
        for p in ROOT.rglob(f"*{source_key}.md"):
            source_file = p
            break
        
        if not source_file:
            print(f"⚠️  Could not find source file for {source_key}")
            continue

        # The target to replace with
        candidate = item["candidates"][0]
        target_fixed = candidate["note_key"]

        # Try to fix common Obsidian link formats: [[target]] or [text](target)
        # We try the most specific broken text first
        success = False
        possible_broken_strings = [
            f"[[{target_broken}]]",
            f"[[{target_broken}|",
            f"({target_broken})",
            target_broken
        ]
        
        possible_fixed_strings = [
            f"[[{target_fixed}]]",
            f"[[{target_fixed}|",
            f"({target_fixed})",
            target_fixed
        ]

        for b, f in zip(possible_broken_strings, possible_fixed_strings):
            if apply_fix(source_file, b, f):
                success = True
                break
        
        if success:
            print(f"✅ Fixed: {source_key} -> {target_broken} replaced by {target_fixed}")
            fixed_count += 1
        else:
            print(f"❌ Failed to apply fix for {source_key} link to {target_broken}")

    print(f"\n=== REPAIR COMPLETE ===")
    print(f"Successfully fixed {fixed_count} links.")

if __name__ == "__main__":
    main()
