"""BPFCoBrain boot-time network detection.

No packages are installed and no downloads are performed.
The result is exposed through environment variables inherited by child
processes launched by launch_app.py.
"""

import os
import urllib.request


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


def configure_environment():
    requested = os.environ.get("BPFCO_BOOT_MODE", "auto").strip().lower()

    if requested not in {"auto", "online", "offline"}:
        requested = "auto"

    if requested == "online":
        mode = "online"
    elif requested == "offline":
        mode = "offline"
    else:
        mode = "online" if internet_available() else "offline"

    os.environ["BPFCO_NETWORK_MODE"] = mode
    os.environ["BPFCO_ONLINE_INTELLIGENCE"] = (
        "1" if mode == "online" else "0"
    )
    # BPFCO_OFFLINE is the hard cloud-fallback block used by OmniRoute.
    # Keep the flag synchronized with the selected boot preference.
    os.environ["BPFCO_OFFLINE"] = "0" if mode == "online" else "1"

    return mode


if __name__ == "__main__":
    mode = configure_environment()
    print(f"BPFCoBrain network mode: {mode.upper()}")
    print(
        "Online intelligence: "
        + ("ENABLED" if mode == "online" else "DISABLED")
    )
