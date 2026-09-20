import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:5001"

checks = [
    ("/super", "SUPER DASHBOARD"),
    ("/brain-graph", "BRAIN GRAPH"),
    ("/vendor/d3.v7.min.js", "LOCAL D3"),
    ("/api/status", "CEO STATUS"),
    ("/api/queue", "TASK QUEUE"),
    ("/api/reports", "AGENT REPORTS"),
    ("/api/plan", "CEO PLAN"),
    ("/api/presence", "PRESENCE"),
    ("/api/activity", "ACTIVITY"),
]

passed = 0

print("=== BPFCo INTEGRATION HEALTH ===")

for path, label in checks:
    try:
        r = urllib.request.urlopen(BASE + path, timeout=3)
        code = r.getcode()

        if code == 200:
            passed += 1
            print(f"PASS  {label}")
        else:
            print(f"FAIL  {label} HTTP {code}")

    except Exception as e:
        print(f"FAIL  {label} :: {e}")

print("")
print(f"RESULT: {passed}/{len(checks)} endpoints responding")

if passed == len(checks):
    print("BPFCo INTEGRATION: PASS")
    raise SystemExit(0)
else:
    print("BPFCo INTEGRATION: ATTENTION REQUIRED")
    raise SystemExit(1)
