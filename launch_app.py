from pathlib import Path
import subprocess
import time
import os
import sys

ROOT = Path(r"C:\BPFCo\BPFCoBrain")
PYTHON = sys.executable

from boot_network import configure_environment

BOOT_MODE = configure_environment()
print(f"[BPFCoBrain] Network mode: {BOOT_MODE.upper()}")
print(
    "[BPFCoBrain] Online intelligence: "
    + ("ENABLED" if BOOT_MODE == "online" else "DISABLED")
)


def run_step(script):
    print(f"[BPFCoBrain] Running {script}...")
    result = subprocess.run(
        [PYTHON, str(ROOT / script)],
        cwd=str(ROOT),
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script} failed with exit code {result.returncode}")
    print(f"[BPFCoBrain] {script}: OK")


print("[BPFCoBrain] Booting CEO executive brain...")

# 1. Verify the shared agent registry/context.
run_step("Shared_Context/integrate_vault.py")

# 2. Build the CEO's current executive state.
run_step("executive_controller.py")

# 3. Refresh the common context snapshot.
run_step("shared_context_bridge.py")

# 4. Generate the CEO startup briefing.
run_step("ceo_startup.py")

# 5. Generate the CEO forward work plan.
run_step("ceo_planner.py")

# 6. Start the existing dashboard.
print("[BPFCoBrain] Starting dashboard...")
dashboard = subprocess.Popen(
    [PYTHON, str(ROOT / "brain-dashboard.py")],
    cwd=str(ROOT),
)

# 7. Open the existing desktop interface.
brain_link = Path(r"C:\Users\Jaques\Desktop\TheBrain 15.lnk")
if brain_link.exists():
    os.startfile(str(brain_link))

# 8. Open the dashboard in Chrome.
time.sleep(2)
chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
if chrome.exists():
    subprocess.Popen([str(chrome), "http://localhost:5000"])

print("")
print("[BPFCoBrain] CEO startup sequence COMPLETE.")
print("[BPFCoBrain] CEO state, shared context, morning report and work plan refreshed.")
print("[BPFCoBrain] External execution remains BLOCKED pending user approval.")
