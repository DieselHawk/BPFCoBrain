"""
BPFCoBrain -> World Monitor MCP integration
Dormant adapter: nothing connects or calls automatically on import.
"""

import json
import os
import time
import urllib.error
import urllib.request


class WorldMonitorMCP:
    def __init__(self, endpoint=None, api_key=None, retries=3, retry_delay=10):
        self.endpoint = (
            endpoint
            or os.getenv("WORLDMONITOR_MCP_URL")
            or "https://worldmonitor.app/mcp"
        )
        self.api_key = api_key or os.getenv("WORLDMONITOR_API_KEY")
        self.retries = retries
        self.retry_delay = retry_delay
        self._request_id = 0

    def _next_id(self):
        self._request_id += 1
        return self._request_id

    def _headers(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.api_key:
            headers["X-WorldMonitor-Key"] = self.api_key
        return headers

    @staticmethod
    def _parse_response(raw):
        text = raw.decode("utf-8", errors="replace").strip()

        # Normal JSON response
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Streamable HTTP / SSE response
        events = []
        for line in text.splitlines():
            if line.startswith("data:"):
                payload = line[5:].strip()
                if not payload:
                    continue
                try:
                    events.append(json.loads(payload))
                except json.JSONDecodeError:
                    continue

        if len(events) == 1:
            return events[0]
        if events:
            return events

        return {"raw": text}

    def rpc(self, method, params=None, timeout=30):
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }

        if params is not None:
            payload["params"] = params

        body = json.dumps(payload).encode("utf-8")

        last_error = None

        for attempt in range(1, self.retries + 1):
            try:
                request = urllib.request.Request(
                    self.endpoint,
                    data=body,
                    headers=self._headers(),
                    method="POST",
                )

                with urllib.request.urlopen(request, timeout=timeout) as response:
                    return self._parse_response(response.read())

            except urllib.error.HTTPError as exc:
                last_error = exc

                # Retry transient server/rate-limit responses.
                if exc.code not in (429, 500, 502, 503, 504):
                    raise

            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = exc

            if attempt < self.retries:
                time.sleep(self.retry_delay)

        raise RuntimeError(
            f"World Monitor MCP request failed after {self.retries} attempts: "
            f"{last_error}"
        )

    def list_tools(self):
        """Discover the live World Monitor MCP tool inventory."""
        return self.rpc("tools/list")

    def call_tool(self, name, arguments=None):
        """Call a World Monitor MCP tool on demand."""
        return self.rpc(
            "tools/call",
            {
                "name": name,
                "arguments": arguments or {},
            },
        )

    def status(self):
        """Local configuration status; performs no network call."""
        return {
            "configured": bool(self.endpoint),
            "endpoint": self.endpoint,
            "api_key_configured": bool(self.api_key),
            "retries": self.retries,
            "retry_delay": self.retry_delay,
        }


if __name__ == "__main__":
    wm = WorldMonitorMCP()
    print(json.dumps(wm.status(), indent=2))
