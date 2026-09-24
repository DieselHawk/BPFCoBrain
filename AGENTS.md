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

## Current-build comparison gate

Before deciding that a new edit is needed, compare the proposal with the
currently running checkout and its uncommitted files. Read the caller and
downstream effects as well as the target file. A clean draft branch or
mergeable PR does not establish compatibility with a dirty live worktree.
If local edits are unavailable, keep the change in a draft and request only
the relevant patch before integration.

For every online/offline edit, trace separate permissions for:
- local Ollama reasoning;
- read-only online research;
- hosted model fallback;
- external actions behind the hardware-backed human approval gate.

Network availability never grants hosted model fallback or permission to
send private prompts. Test Ollama failure while online to verify this.
Agents may converse, research, draft and learn internally without approval.
Do not add paid dependencies or make the core depend on an online service.

Use actual task/report copies in an isolated worktree when available. Compare
API counts and the visible dashboard with the baseline, and preserve a
reversible path for any preview mutation. Keep graph/Meeting work separate
from unfinished connectors. Do not merge until the uncommitted executive
graph adapter is reviewed and the integrated branch reproduces the verified
executive and provenance links.
