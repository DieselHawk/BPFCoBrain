# BPFCo Presence Adapter
# Renderer-neutral contract for Fred, Bob, Cindy, Kai and Neo.
# No external dependencies.

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os

AGENTS = {
    "Fred":  {"role":"CEO",       "voice_env":"BPFCO_FRED_VOICE",  "voice":"male",   "color":"#78c8ef", "personality":"calm strategic commander"},
    "Bob":   {"role":"Finance",   "voice_env":"BPFCO_BOB_VOICE",   "voice":"male",   "color":"#65d6a6", "personality":"precise financial analyst"},
    "Cindy": {"role":"Secretary", "voice_env":"BPFCO_CINDY_VOICE", "voice":"female", "color":"#ef8fcb", "personality":"warm organised coordinator"},
    "Kai":   {"role":"Legal",     "voice_env":"BPFCO_KAI_VOICE",   "voice":"male",   "color":"#c7a3ff", "personality":"measured legal investigator"},
    "Neo":   {"role":"Sales",     "voice_env":"BPFCO_NEO_VOICE",   "voice":"male",   "color":"#ffb45f", "personality":"energetic commercial scout"},
}

STATES = {
    "IDLE",
    "READY",
    "QUEUED",
    "WORKING",
    "PRESENT",
    "LISTENING",
    "THINKING",
    "SPEAKING",
}

EVENTS = {
    "call",
    "return",
    "listen",
    "think",
    "speak",
    "handoff",
    "greeting",
}

@dataclass
class PresenceFrame:
    agent: str
    role: str
    state: str
    event: str
    voice: str
    renderer: str
    lip_sync: bool
    motion: bool
    expression: str
    color: str
    personality: str
    greeting: str

def make_frame(agent, state="IDLE", event="none"):
    if agent not in AGENTS:
        raise ValueError(f"unknown agent: {agent}")
    if state not in STATES:
        raise ValueError(f"unknown state: {state}")

    meta = AGENTS[agent]

    expression = {
        "IDLE":"neutral",
        "READY":"attentive",
        "QUEUED":"attentive",
        "WORKING":"focused",
        "PRESENT":"attentive",
        "LISTENING":"listening",
        "THINKING":"thinking",
        "SPEAKING":"speaking",
    }[state]

    return PresenceFrame(
        agent=agent,
        role=meta["role"],
        state=state,
        event=event,
        voice=os.getenv(meta["voice_env"], meta["voice"]),
        renderer=os.getenv("BPFCO_PRESENCE_RENDERER", "vrm"),
        lip_sync=(state == "SPEAKING"),
        motion=(state not in {"IDLE","READY"}),
        expression=expression,
        color=meta["color"],
        personality=meta["personality"],
        greeting=f"{agent} online. {meta['role']} station ready.",
    )

def write_frame(frame, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(frame), indent=2),
        encoding="utf-8"
    )

if __name__ == "__main__":
    f = make_frame("Fred", "SPEAKING", "speak")
    print("BPFCo PRESENCE ADAPTER: PASS")
    print(json.dumps(asdict(f), indent=2))
