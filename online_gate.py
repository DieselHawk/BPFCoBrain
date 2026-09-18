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

    def select_tool(self, query, tools, agent_name="", role=""):
        """
        Deterministic intent-first World Monitor routing.

        Priority:
        1. Explicit task intent
        2. Agent role as supporting context
        3. Live tool descriptions as fallback

        Only tools advertised by the live MCP server can be selected.
        """

        text = str(query).lower()

        available = {
            str(tool.get("name")): tool
            for tool in tools
            if isinstance(tool, dict) and tool.get("name")
        }

        # Strong, explicit routing rules.
        INTENT_RULES = [
            (
                ("diesel", "fuel", "petrol", "gasoline", "energy",
                 "electricity", "gas storage", "oil supply"),
                "get_energy_intelligence",
            ),
            (
                ("market", "stock price", "share price", "commodity price",
                 "oil price", "gold price", "silver price", "forex",
                 "fx", "crypto", "equity"),
                "get_market_data",
            ),
            (
                ("tender", "tenders", "procurement", "public procurement",
                 "bid opportunity", "contract opportunity"),
                "get_procurement_opportunities",
            ),
            (
                ("sanction", "sanctions", "ofac", "sdn"),
                "get_sanctions_data",
            ),
            (
                ("conflict", "war", "armed conflict", "military attack",
                 "missile", "ceasefire", "unrest", "invasion"),
                "get_conflict_events",
            ),
            (
                ("cyber", "ransomware", "malware", "cve",
                 "cyber attack", "hack", "hacking"),
                "get_cyber_threats",
            ),
            (
                ("aviation", "airspace", "airport", "flight",
                 "flights", "notam"),
                "get_aviation_status",
            ),
            (
                ("shipping", "maritime", "vessel", "port",
                 "chokepoint", "strait"),
                "get_chokepoint_status",
            ),
            (
                ("economy", "economic", "gdp", "inflation",
                 "interest rate", "central bank", "macro"),
                "get_economic_data",
            ),
            (
                ("country risk", "country instability",
                 "country resilience"),
                "get_country_risk",
            ),
            (
                ("geopolitical news", "geopolitical developments",
                 "latest geopolitical", "breaking geopolitical",
                 "latest news", "breaking news", "current news",
                 "recent news"),
                "get_news_intelligence",
            ),
            (
                ("world brief", "global situation",
                 "global developments", "world situation"),
                "get_world_brief",
            ),
        ]

        # First matching explicit intent wins.
        for keywords, tool_name in INTENT_RULES:
            if tool_name not in available:
                continue

            for keyword in keywords:
                if keyword in text:
                    print(
                        f"[*] Online route: "
                        f"{agent_name or 'generic'} -> {tool_name}"
                    )
                    return tool_name

        # Role-aware fallback only when no explicit intent matched.
        role_text = f"{agent_name} {role}".lower()

        ROLE_HINTS = {
            "sales": (
                "procurement", "tender", "business",
                "company", "companies", "commercial"
            ),
            "finance": (
                "market", "commodity", "economic",
                "oil", "energy", "financial"
            ),
            "legal": (
                "sanction", "country risk", "policy",
                "conflict", "cyber"
            ),
            "secretary": (
                "news", "aviation", "maritime",
                "alerts", "economic"
            ),
            "executive": (
                "world brief", "global", "risk",
                "economic", "geopolitical"
            ),
        }

        fallback_candidates = []

        for tool_name, tool in available.items():
            haystack = (
                f"{tool_name} "
                f"{tool.get('description', '')}"
            ).lower()

            score = 0

            for role_key, hints in ROLE_HINTS.items():
                if role_key in role_text:
                    for hint in hints:
                        if hint in haystack:
                            score += 1

            if score:
                fallback_candidates.append(
                    (score, tool_name)
                )

        if fallback_candidates:
            fallback_candidates.sort(
                key=lambda item: item[0],
                reverse=True,
            )
            selected = fallback_candidates[0][1]

            print(
                f"[*] Online role fallback: "
                f"{agent_name or 'generic'} -> {selected}"
            )

            return selected

        # Final safe fallback.
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




