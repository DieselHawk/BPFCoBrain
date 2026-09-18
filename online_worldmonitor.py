"""
BPFCoBrain Online Intelligence Gateway

World Monitor is intentionally NOT part of normal Brain startup.
This module is invoked explicitly when online intelligence is required.
"""

from worldmonitor_mcp import WorldMonitorMCP


def worldmonitor_status():
    wm = WorldMonitorMCP()
    return wm.status()


def worldmonitor_tools():
    wm = WorldMonitorMCP()
    return wm.list_tools()


def worldmonitor_call(tool_name, arguments=None):
    wm = WorldMonitorMCP()
    return wm.call_tool(tool_name, arguments or {})


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Optional online World Monitor gateway"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")

    tools = sub.add_parser("tools")

    call = sub.add_parser("call")
    call.add_argument("tool")
    call.add_argument("--arguments", default="{}")

    args = parser.parse_args()

    if args.command == "status":
        print(json.dumps(worldmonitor_status(), indent=2))

    elif args.command == "tools":
        print(json.dumps(worldmonitor_tools(), indent=2))

    elif args.command == "call":
        arguments = json.loads(args.arguments)
        print(
            json.dumps(
                worldmonitor_call(args.tool, arguments),
                indent=2
            )
        )
