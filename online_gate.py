"""
BPFCoBrain Online Intelligence Gate

Online-only capability.
Normal Brain operation remains offline-first.
World Monitor tools are discovered dynamically.
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
        r"market|price|prices|risk|alert|outage|shipping|"
        r"geopolit|forecast|trend"
        r")\b",
        re.IGNORECASE,
    )

    ROUTES = [
        (
            "energy",
            (
                "diesel", "fuel", "petrol", "gasoline", "oil",
                "energy", "electricity", "gas", "renewable"
            ),
            "get_energy_intelligence",
        ),
        (
            "market",
            (
                "market", "stock", "equity", "commodity", "gold",
                "silver", "forex", "fx", "crypto", "share price"
            ),
            "get_market_data",
        ),
        (
            "economy",
            (
                "economy", "economic", "macro", "inflation",
                "interest rate", "fed", "ecb", "gdp"
            ),
            "get_economic_data",
        ),
        (
            "conflict",
            (
                "war", "conflict", "attack", "military", "missile",
                "ceasefire", "unrest", "protest", "invasion"
            ),
            "get_conflict_events",
        ),
        (
            "cyber",
            (
                "cyber", "ransomware", "malware", "hack",
                "vulnerability", "cve", "c2"
            ),
            "get_cyber_threats",
        ),
        (
            "maritime",
            (
                "shipping", "maritime", "vessel", "port",
                "chokepoint", "strait", "ship"
            ),
            "get_chokepoint_status",
        ),
        (
            "aviation",
            (
                "aviation", "airspace", "airport",
                "flight", "flights", "notam"
            ),
            "get_aviation_status",
        ),
        (
            "procurement",
            (
                "tender", "tenders", "procurement",
                "contract opportunity", "bid opportunity"
            ),
            "get_procurement_opportunities",
        ),
        (
            "sanctions",
            (
                "sanction", "sanctions", "ofac", "sdn"
            ),
            "get_sanctions_data",
        ),
        (
            "news",
            (
                "news", "latest", "breaking", "current",
                "today", "recent", "update", "updated"
            ),
            "get_news_intelligence",
        ),
        (
            "world",
            (
                "world", "global", "geopolitical",
                "global situation", "world situation"
            ),
            "get_world_brief",
        ),
    ]

    def __init__(self):
        self.enabled = os.getenv(
            "BPFCO_ONLINE_INTELLIGENCE", "0"
        ) == "1"

        self.world_monitor = WorldMonitorMCP()
        self._tools = None

    def needs_online(self, text):
        """Local-only detection. Never contacts the network."""
        if not text:
            return False

        return bool(self.CURRENT_TERMS.search(str(text)))

    def status(self):
        return {
            "online_intelligence_enabled": self.enabled,
            "worldmonitor_endpoint": self.world_monitor.endpoint,
            "api_key_configured": bool(self.world_monitor.api_key),
        }

    def discover_tools(self):
        """
        Discover the live World Monitor MCP inventory.
        Discovery itself is public.
        """
        if self._tools is not None:
            return self._tools

        response = self.world_monitor.list_tools()

        tools = (
            response.get("result", {}).get("tools", [])
            if isinstance(response, dict)
            else []
        )

        self._tools = tools
        return tools

    def select_tool(self, query, tools):
        """
        Choose a suitable tool from the LIVE discovered inventory.
        Never selects a tool that the server did not advertise.
        """
        available = {
            tool.get("name")
            for tool in tools
            if isinstance(tool, dict)
        }

        text = str(query).lower()

        for _, keywords, tool_name in self.ROUTES:
            if tool_name not in available:
                continue

            if any(keyword in text for keyword in keywords):
                return tool_name

        if "get_news_intelligence" in available:
            return "get_news_intelligence"

        if "get_world_brief" in available:
            return "get_world_brief"

        return None

    def build_arguments(self, tool_name, query):
        """
        Only send arguments known to be appropriate for the selected tool.
        """
        if tool_name == "get_news_intelligence":
            return {
                "query": str(query),
                "limit": 6,
            }

        if tool_name == "get_market_data":
            return {
                "limit": 6,
            }

        if tool_name == "get_energy_intelligence":
            return {
                "limit": 6,
            }

        if tool_name == "get_economic_data":
            return {
                "summary": True,
            }

        if tool_name == "get_conflict_events":
            return {
                "limit": 6,
            }

        if tool_name == "get_cyber_threats":
            return {
                "limit": 6,
            }

        if tool_name == "get_aviation_status":
            return {
                "limit": 6,
            }

        if tool_name == "get_procurement_opportunities":
            return {
                "query": str(query),
                "limit": 6,
            }

        if tool_name == "get_sanctions_data":
            return {
                "query": str(query),
                "limit": 6,
            }

        # Tools requiring structured geographic parameters
        # are not guessed from free text.
        return {}

    def research(self, query):
        """
        Explicit online intelligence request.

        Offline mode always wins.
        """
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

        try:
            tools = self.discover_tools()
        except Exception as exc:
            return {
                "status": "discovery_error",
                "error": f"{type(exc).__name__}: {exc}",
            }

        tool_name = self.select_tool(query, tools)

        if not tool_name:
            return {
                "status": "no_suitable_tool",
                "discovered_tools": len(tools),
            }

        if not self.world_monitor.api_key:
            return {
                "status": "not_configured",
                "reason": "WORLDMONITOR_API_KEY is not configured",
                "selected_tool": tool_name,
                "discovered_tools": len(tools),
            }

        try:
            result = self.world_monitor.call_tool(
                tool_name,
                self.build_arguments(tool_name, query),
            )

            return self._compact(
                result,
                tool_name,
            )

        except Exception as exc:
            return {
                "status": "error",
                "tool": tool_name,
                "error": f"{type(exc).__name__}: {exc}",
            }

    @staticmethod
    def _compact(result, tool_name):
        if isinstance(result, dict):
            content = result.get("result", {}).get("content")

            if isinstance(content, list) and content:
                text = content[0].get("text", "")

                try:
                    parsed = json.loads(text)

                    return {
                        "status": "success",
                        "tool": tool_name,
                        "data": parsed,
                    }

                except (TypeError, json.JSONDecodeError):
                    return {
                        "status": "success",
                        "tool": tool_name,
                        "data": str(text)[:12000],
                    }

        return {
            "status": "success",
            "tool": tool_name,
            "data": result,
        }
