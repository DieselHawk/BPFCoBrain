# BPFCo Presence Adapter
# Renderer-neutral contract for Fred, Bob, Cindy, Kai and Neo.
# No external dependencies.

from dataclasses import dataclass, asdict
from pathlib import Path
import json

AGENTS = {
    "Fred":  {"role":"CEO",       "voice":"male",   "renderer":"vrm"},
    "Bob":   {"role":"Finance",   "voice":"male",   "renderer":"vrm"},
    "Cindy": {"role":"Secretary", "voice":"female", "renderer":"vrm"},
    "Kai":   {"role":"Legal",     "voice":"male",   "renderer":"vrm"},
    "Neo":   {"role":"Sales",     "voice":"male",   "renderer":"vrm"},
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
        voice=meta["voice"],
        renderer=meta["renderer"],
        lip_sync=(state == "SPEAKING"),
        motion=(state not in {"IDLE","READY"}),
        expression=expression,
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
