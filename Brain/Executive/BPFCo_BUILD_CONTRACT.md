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

## ARCHITECTURE MANDATE — GIT COMPONENT HARVEST

BPFCoBrain remains the authoritative brain and orchestration system.

The BPFCo Super Dashboard must preferentially USE and ADAPT proven open-source Git components rather than re-implement mature dashboard features.

Primary dashboard reference:
- builderz-labs/mission-control
  - agent fleet
  - task lifecycle
  - live activity
  - memory/relationship graph
  - approvals/audit
  - REST/OpenAPI
  - WebSocket/SSE
  - local SQLite

Secondary visual references/components may be harvested from suitable open-source projects.

Presence:
- ARPAHLS/avatar remains the preferred VRM rendering/stage candidate.
- AILIS and ELINO remain architectural/component references.
- Presence serves Fred, Bob, Cindy, Kai and Neo.
- BPFCoBrain remains in control of identity, state, permissions and orchestration.

RULE:
Do not pull or install large dependencies on mobile data.
Heavy Git/npm/pnpm/model/avatar downloads are Wi-Fi-only.

RULE:
Do not replace existing BPFCoBrain functionality with an external project.
Integrate useful proven components behind BPFCo interfaces.

TARGET:
Build toward a polished BPFCo Command Center with:
agent fleet + tasks + handoffs + approvals + audit + knowledge graph + system health + live activity + presence + five-agent staff meeting mode.

Future sessions MUST continue toward this target and MUST NOT restart the architecture.

# SUPER BRAIN VISUAL MANDATE

The BPFCo Super Dashboard is a spatial "Super Brain" interface.

Visual target:
- deep starfield / space background
- central BPFCo knowledge universe
- smooth zoom/orbit navigation
- distant high-level domains
- zoom-in reveals documents, nodes and relationships
- further zoom reveals connected content
- graph is driven by BPFCoBrain data, not invented dashboard data

Git component strategy:
Prefer proven open-source Git components over reimplementing mature visual systems.

Primary visual reference/component:
- 3d-force-graph
  Use/adapt its proven 3D force graph, camera, links, particles and node interaction.

Secondary visual reference/component:
- ReverySky-style spatial vault visualization
  Use/adapt the concept of a starfield knowledge universe with zoom/fly-to-node and graph prominence.

Additional reference:
- RepoMind-AI-style layered drill-down
  Galaxy -> domains -> files -> deeper relationships.

BPFCoBrain remains authoritative.
Third-party components are renderers/building blocks only.

AGENT PRESENCE

Calling an agent must bring that agent into a face-to-face human-facing presence layer.

Agents:
- Fred — CEO
- Bob — Finance
- Cindy — Secretary
- Kai — Legal
- Neo — Sales

Presence target:
- distinct face/identity
- distinct voice
- speaking/listening state
- expression
- animation
- lip-sync
- shared staff-meeting room
- agent can be called from the Super Brain

Preferred renderer direction:
- VRM-capable avatar runtime
- ARPAHLS/avatar remains a renderer/stage candidate
- AILIS / ELINO remain reference sources for useful presence architecture

The brain decides WHAT happens.
The dashboard visualizes it.
The presence layer makes it human-facing.
The renderer displays it.

HUMAN APPROVAL SECURITY MANDATE

External execution remains human-controlled.

Approval flow:
1. Agent requests approval.
2. Terminal presents the approval request.
3. Human must provide the approval input.
4. Security hardware must be present.
5. Hardware-backed key/challenge validation must succeed.
6. Only then may the approval be accepted.
7. Without valid hardware, terminal approval MUST be rejected.

USB security requirement:
- Do NOT rely on a plain file existing on the USB.
- Use a cryptographic key/challenge-response mechanism.
- USB presence is necessary but not sufficient.
- Secret material must not be exposed through ordinary filesystem copying.

This hardware gate applies before external execution.

DEPENDENCY / DATA POLICY

Mobile data:
- architecture
- local code
- configuration
- small Git commits

Wi-Fi only:
- large Git repositories
- npm/pnpm dependency trees
- Electron runtimes
- avatar runtimes
- VRM assets
- ASR/TTS packages
- AI models

Do not pull large dependencies merely to prototype the architecture.

IMPLEMENTATION ORDER

1. Preserve existing BPFCoBrain.
2. Use existing CEO/agent/dashboard infrastructure.
3. Connect Super Brain visualization directly to BPFCoBrain's existing index/relationships.
4. Add proven Git visual components behind adapters.
5. Add Presence API.
6. Add agent identity/voice/avatar adapters.
7. Add staff-meeting mode.
8. Implement cryptographic USB approval gate.
9. Integrate heavy dependencies on Wi-Fi.
10. Keep every stable milestone committed and pushed.

COURSE-CORRECTION RULE

Before implementing a subsystem, search existing BPFCoBrain files and suitable Git projects for an existing capability.

Reuse > adapt > write new code.

Never rebuild a mature capability merely because it is easier to write locally.

CONTINUITY

Any future session reading this repository must continue this architecture.

Do not restart the project.
Do not replace BPFCoBrain.
Do not create parallel dashboard systems when an existing BPFCoBrain dashboard can be extended.
