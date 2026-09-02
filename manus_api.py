"""Minimal direct Manus API client for BPFCoBrain."""

import json
import os
import urllib.error
import urllib.request


class ManusApiError(RuntimeError):
    pass


def create_task(prompt, title="BPFCoBrain context", profile="manus-1.6-lite"):
    """Create a private Manus task using MANUS_API_KEY and return its identifiers."""
    api_key = os.environ.get("MANUS_API_KEY")
    if not api_key:
        raise ManusApiError("MANUS_API_KEY is not configured")
    payload = {
        "message": {"content": prompt},
        "title": title,
        "agent_profile": profile,
        "share_visibility": "private",
        "interactive_mode": True,
    }
    request = urllib.request.Request(
        "https://api.manus.ai/v2/task.create",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-manus-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ManusApiError(f"Manus API request failed: {exc}") from exc
    if not result.get("ok"):
        error = result.get("error", {})
        raise ManusApiError(error.get("message", "Manus API returned an error"))
    return result
