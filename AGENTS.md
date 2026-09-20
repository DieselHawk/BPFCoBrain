# BPFCoBrain Agent Instructions

THIS REPOSITORY IS AN EXISTING WORKING SYSTEM. DO NOT REBUILD IT.

Before changing anything:
1. Read `Brain/Executive/BPFCo_BUILD_CONTRACT.md`.
2. Read `Brain/Executive/BPFCo_SESSION_START_PROMPT.md`.
3. Inspect the actual Git/machine state.
4. Continue from the existing implementation.

Core authority:
BPFCoBrain remains the authoritative brain and orchestration layer.

Architecture:
BPFCoBrain
 -> CEO/Fred
 -> Agent Runtime
 -> OmniRoute
 -> Bob / Cindy / Kai / Neo
 -> Knowledge / document lattice
 -> Approval Gate
 -> Rollover / continuity
 -> local Ollama/Hermes
 -> optional WorldMonitor

Future presentation:
BPFCo Super Dashboard
 -> Presence Layer
 -> agent identity / voice / emotion / motion
 -> avatar renderer
 -> Fred / Bob / Cindy / Kai / Neo

Do not replace the brain with an outside project.
Use Git projects as isolated building blocks or references.
Prefer local/offline operation.
Keep human approval gates intact.
Do not introduce paid/cloud dependencies into the core.
Do not download large dependencies on mobile data.

Build style:
- incremental changes
- modular commits
- verify before changing
- preserve working functionality
- commit and push completed milestones
- never silently overwrite existing work
- never rebuild something that already exists

When work is resumed:
continue the planned build from the repository state instead of restarting the project.
