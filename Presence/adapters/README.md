# BPFCo → ELINO Presence Mapping

BPFCoBrain owns:
- agent identity
- state
- task status
- permissions
- event
- approval state

Presence adapter translates that into renderer-neutral frames.

Renderer later consumes:
agent
role
state
event
voice
renderer
lip_sync
motion
expression

Current renderer target:
ELINO harvested VRM / lip-sync / motion components.

Future:
Replace adapter output target with the selected VRM runtime.
Do not import ELINO LLM, prompt, memory, or orchestration layers.

State mapping:
IDLE       -> neutral
READY      -> attentive
QUEUED     -> attentive
WORKING    -> focused
PRESENT    -> attentive
LISTENING  -> listening
THINKING   -> thinking
SPEAKING   -> speaking + lip-sync
