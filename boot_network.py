"""BPFCoBrain boot-time network detection.

No packages are installed and no downloads are performed.
The result is exposed through environment variables inherited by child
processes launched by launch_app.py.
"""

import json
import os
from pathlib import Path
import urllib.request


MODE_FILE = Path(__file__).resolve().parent / "Brain" / "Executive" / "network_mode.json"

PROBE_URLS = (
    "https://www.google.com/generate_204",
    "https://www.cloudflare.com/",
)


def internet_available(timeout=3):
    for url in PROBE_URLS:
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "BPFCoBrain/boot-check"},
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if 200 <= response.status < 400:
                    return True
        except Exception:
            continue
    return False


def saved_preference():
    try:
        value = json.loads(MODE_FILE.read_text(encoding="utf-8")).get("mode")
    except (OSError, ValueError, AttributeError):
        return None
    return value if value in {"online", "offline"} else None


def set_mode(mode):
    if mode not in {"online", "offline"}:
        raise ValueError("Choose online or offline")
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = MODE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps({"mode": mode}), encoding="utf-8")
    temporary.replace(MODE_FILE)
    os.environ["BPFCO_NETWORK_MODE"] = mode
    os.environ["BPFCO_ONLINE_INTELLIGENCE"] = "1" if mode == "online" else "0"
    os.environ["BPFCO_OFFLINE"] = "0" if mode == "online" else "1"
    return mode


def configure_environment():
    requested = os.environ.get("BPFCO_BOOT_MODE", "auto").strip().lower()
    if requested == "auto":
        requested = saved_preference() or "auto"

    if requested not in {"auto", "online", "offline"}:
        requested = "auto"

    if requested == "online":
        mode = "online"
    elif requested == "offline":
        mode = "offline"
    else:
        mode = "online" if internet_available() else "offline"

    # Boot selection is transient. Only an explicit dashboard toggle is persisted.
    os.environ["BPFCO_NETWORK_MODE"] = mode
    os.environ["BPFCO_ONLINE_INTELLIGENCE"] = "1" if mode == "online" else "0"
    os.environ["BPFCO_OFFLINE"] = "0" if mode == "online" else "1"
    return mode


if __name__ == "__main__":
    mode = configure_environment()
    print(f"BPFCoBrain network mode: {mode.upper()}")
    print(
        "Online intelligence: "
        + ("ENABLED" if mode == "online" else "DISABLED")
    )
