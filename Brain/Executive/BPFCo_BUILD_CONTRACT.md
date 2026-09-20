# BPFCoBrain Build Contract

## Mission
Continue the existing BPFCoBrain build as an incremental local-first AI operating system.

## Non-negotiables

### 1. Preserve the existing brain
The current CEO, agent runtime, OmniRoute, document lattice, approval gate, rollover system, and local Ollama/Hermes integration are existing assets.

Never replace them merely to adopt an outside project.

### 2. Agent structure
The staff consists of:
- Fred — CEO
- Bob — Finance
- Cindy — Secretary
- Kai — Legal
- Neo — Sales

All specialists report to Fred.

### 3. Continuity
At startup:
- inspect previous unfinished work
- restore rollover tasks
- continue unfinished work
- escalate stuck work for human/ChatGPT assistance
- preserve the next-day queue

### 4. Safety and control
External execution remains human-gated.
Cloud services must not become core dependencies.
Offline/local operation is the default.

### 5. Presence architecture
The visual system is an additional layer:

BPFCoBrain
  -> Presence Controller
  -> Agent Identity
  -> Voice
  -> Expression / Motion
  -> Avatar Renderer

The current avatar direction is:
- VRM-capable rendering
- lip-sync
- animation
- distinct identity per agent
- shared runtime
- staff-meeting mode

ARPAHLS AVATAR is a renderer/stage candidate.
AILIS and ELINO are architectural references.
They do not become the BPFCoBrain authority.

### 6. Super Dashboard
Build a BPFCo-specific command center showing:
- agent fleet
- agent flow / handoffs
- tasks
- approvals
- knowledge lattice
- system health
- live activity
- staff meeting mode
- presence/avatar status

The dashboard is a visualization/control layer over BPFCoBrain, not a second brain.

### 7. Dependency policy
Mobile data is reserved for small source/configuration changes.

Large downloads are Wi-Fi-only:
- npm/pnpm environments
- Electron runtimes
- avatar installers
- VRM assets
- ASR/TTS packages
- model files

Never start a multi-hundred-MB or multi-GB download without explicitly identifying its size and purpose.

### 8. Git discipline
Use small logical commits.
Before edits, inspect state.
After a completed milestone:
git add <target files>
git commit -m "<logical change>"
git push origin main

Never use destructive reset/checkout commands unless explicitly required.

### 9. Resume rule
A future agent reading this repository must treat this document as the architectural contract and continue from the current implementation state.

Do not restart the project.
Do not ask the user to repeat information already encoded in the repository.
Do not substitute a different architecture merely because a new Git project is available.
