"""
BPFCoBrain Online Intelligence Gate

World Monitor is optional and online-only.
Normal/offline Brain operation never calls it.
"""

import json
import os
import re

from worldmonitor_mcp import WorldMonitorMCP


class OnlineGate:
    CURRENT_TERMS = re.compile(
        r"\b("
        r"latest|today|current|currently|now|live|breaking|recent|"
        r"this week|this month|updated|update|news|developing|"
        r"market|price|prices|risk|alert|outage|shipping|geopolit"
        r")\b",
        re.IGNORECASE,
    )

    def __init__(self):
        self.enabled = os.getenv("BPFCO_ONLINE_INTELLIGENCE", "0") == "1"
        self.world_monitor = WorldMonitorMCP()

    def needs_online(self, text):
        """Local-only detection. No network call."""
        if not text:
            return False
        return bool(self.CURRENT_TERMS.search(str(text)))

    def status(self):
        return {
            "online_intelligence_enabled": self.enabled,
            "worldmonitor_endpoint": self.world_monitor.endpoint,
            "api_key_configured": bool(self.world_monitor.api_key),
        }

    def research(self, query):
        """
        Explicit online request.
        Returns a compact result and fails safely.
        """
        # Hard safety gate: offline Brain never contacts World Monitor.
        if os.getenv("BPFCO_OFFLINE") == "1":
            return {
                "status": "disabled",
                "reason": "BPFCO_OFFLINE=1",
            }

        if not self.enabled:
            return {
                "status": "disabled",
                "reason": "BPFCO_ONLINE_INTELLIGENCE is not enabled",
            }

        if not self.world_monitor.api_key:
            return {
                "status": "not_configured",
                "reason": "WORLDMONITOR_API_KEY is not configured",
            }

        try:
            result = self.world_monitor.call_tool(
                "get_news_intelligence",
                {
                    "query": str(query),
                    "limit": 6,
                },
            )

            return self._compact(result)

        except Exception as exc:
            return {
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
            }

    @staticmethod
    def _compact(result):
        """
        Keep MCP output small before returning it to an agent.
        """
        if isinstance(result, dict):
            content = result.get("result", {}).get("content")

            if isinstance(content, list) and content:
                text = content[0].get("text", "")
                try:
                    parsed = json.loads(text)
                    return {
                        "status": "success",
                        "data": parsed,
                    }
                except (TypeError, json.JSONDecodeError):
                    return {
                        "status": "success",
                        "data": str(text)[:12000],
                    }

        return {
            "status": "success",
            "data": result,
        }


