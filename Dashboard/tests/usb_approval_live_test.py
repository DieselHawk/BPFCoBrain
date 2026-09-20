import json
import time
from pathlib import Path

import approval_gate

print("=== BPFCo AUTOMATED USB APPROVAL TEST ===")
print("")
print("1. Test approval will be created.")
print("2. Script will wait automatically for the USB.")
print("3. Insert the BPFCo USB when ready.")
print("4. Validation will occur automatically.")
print("5. You press ENTER to complete approval.")
print("")

record = approval_gate.request(
    "BPFCo_AUTOMATED_USB_TEST",
    agent="Fred",
    payload={"test": True}
)

approval_id = record["approval_id"]

print("TEST APPROVAL:", approval_id)
print("")

try:
    result = approval_gate.approve_interactive(
        approval_id,
        poll_seconds=1,
        timeout_seconds=None
    )

    approved = approval_gate.is_approved(approval_id)

    if not approved:
        raise RuntimeError(
            "Approval returned but Approved record was not found."
        )

    print("")
    print("USB TEST: PASS")
    print("FINAL STATUS:", result["status"])
    print("APPROVAL METHOD:", result["approval_method"])

except KeyboardInterrupt:
    print("")
    print("TEST STOPPED BY HUMAN")
    raise

except Exception as exc:
    print("")
    print("USB TEST: FAIL")
    print(type(exc).__name__ + ":", exc)
    raise
