"""Isolated local-first agent terminal routes.

This blueprint deliberately does not modify or render the Super dashboard.
"""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file


ROOT = Path(__file__).resolve().parents[1]
EXECUTIVE = ROOT / "Brain" / "Executive"
PRESENCE_FILE = EXECUTIVE / "presence_state.json"
PERSONA_DIR = EXECUTIVE / "Personas"

AGENTS = {
    "Fred": {"role": "CEO", "color": "#78c8ef"},
    "Bob": {"role": "Finance", "color": "#65d6a6"},
    "Cindy": {"role": "Secretary", "color": "#ef8fcb"},
    "Kai": {"role": "Legal", "color": "#c7a3ff"},
    "Neo": {"role": "Sales", "color": "#ffb45f"},
}

AVATAR_DIR = ROOT / "Dashboard" / "assets" / "agents"

agent_terminal_bp = Blueprint("agent_terminal", __name__)


def write_presence(agent, state, event):
    PRESENCE_FILE.write_text(
        json.dumps({"agent": agent, "state": state, "event": event}, indent=2),
        encoding="utf-8",
    )


def local_reply(agent, message):
    persona_path = PERSONA_DIR / f"{agent.lower()}.md"
    persona = (
        persona_path.read_text(encoding="utf-8", errors="ignore")
        if persona_path.exists()
        else f"You are {agent}, the BPFCoBrain {AGENTS[agent]['role']} agent."
    )
    prompt = (
        f"SYSTEM PERSONA:\n{persona}\n\n"
        "You are speaking inside the BPFCoBrain local terminal. Be concise. "
        "Never claim an external action was executed; external actions require human approval.\n\n"
        f"USER:\n{message}"
    )
    payload = json.dumps({
        "model": os.environ.get("BPFCO_OLLAMA_MODEL", "hermes3:8b"),
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"num_predict": 384, "temperature": 0.2},
    }).encode("utf-8")
    ollama_url = os.environ.get(
        "BPFCO_OLLAMA_URL", "http://127.0.0.1:11434/api/chat"
    )
    ollama_request = urllib.request.Request(
        ollama_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(ollama_request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result.get("message", {}).get("content", "").strip()


@agent_terminal_bp.route("/agent-terminal/terminal.css")
def agent_terminal_css():
    return send_file(ROOT / "Dashboard" / "components" / "agent_terminal.css")


@agent_terminal_bp.route("/agent-terminal/terminal.js")
def agent_terminal_js():
    return send_file(ROOT / "Dashboard" / "components" / "agent_terminal.js")


@agent_terminal_bp.route("/agent-terminal/avatar/<agent>.webp")
def agent_terminal_avatar(agent):
    name = agent.strip().title()
    if name not in AGENTS:
        return jsonify({"ok": False, "error": "Unknown agent"}), 404
    return send_file(AVATAR_DIR / f"{name.lower()}.webp", mimetype="image/webp")


@agent_terminal_bp.route("/api/agent-terminal/status")
def agent_terminal_status():
    mode = os.environ.get("BPFCO_NETWORK_MODE", "offline").lower()
    return jsonify({
        "ok": True,
        "network_mode": mode,
        "renderer": "vrm-3d" if mode == "online" else "css-2d",
        "agents": {
            name: {
                **meta,
                "avatar": f"/agent-terminal/avatar/{name.lower()}.webp",
            }
            for name, meta in AGENTS.items()
        },
    })


@agent_terminal_bp.route("/api/agent-terminal/interact", methods=["POST"])
def agent_terminal_interact():
    data = request.get_json(silent=True) or {}
    agent = str(data.get("agent", "")).strip()
    message = str(data.get("message", "")).strip()

    if agent not in AGENTS:
        return jsonify({"ok": False, "error": "Unknown agent"}), 400
    if not message:
        return jsonify({"ok": False, "error": "Message is required"}), 400
    if len(message) > 4000:
        return jsonify({"ok": False, "error": "Message is too long"}), 400

    write_presence(agent, "THINKING", "think")
    try:
        answer = local_reply(agent, message)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        write_presence(agent, "PRESENT", "call")
        return jsonify({
            "ok": False,
            "error": f"Local model unavailable: {type(exc).__name__}",
        }), 503

    if not answer:
        write_presence(agent, "PRESENT", "call")
        return jsonify({"ok": False, "error": "Local model returned no response"}), 503

    write_presence(agent, "SPEAKING", "speak")
    return jsonify({"ok": True, "agent": agent, "response": answer, "mode": "local"})
