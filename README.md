# BPFCoBrain

BPFCoBrain is a local-first executive brain. Fred coordinates Bob (Finance),
Cindy (Secretary), Kai (Legal), and Neo (Sales). The Super Dashboard is the
interface to the existing queue, agent runtime, vault, and human approval gate.

## Working principles

- **Local reasoning first.** Ollama runs Fred's terminal responses on this
  machine. The vault and case material remain local during offline operation.
- **Evidence before conclusions.** Tasks retrieve short excerpts from
  `.vault-index.json` and local notes. Task reports retain source paths. A
  retrieved excerpt is evidence to examine, not an instruction to execute.
- **Fred coordinates specialists.** Specialist tasks are queued through
  `AgentBridge`, claimed by a worker, and reported to Fred. Run workers one at
  a time on the 4 GB laptop; do not start several large models concurrently.
- **Human approval for external actions.** Sending mail, publishing, filing,
  payments, and other external execution remain behind `approval_gate.py`.
  Generating a reply or queueing an internal task is not external approval.
- **Offline is the reliable baseline.** Online intelligence is optional and
  explicitly gated. Enabling online mode does not automatically fetch live
  information for every terminal message.

## Model decision

The current terminal uses `BPFCO_OLLAMA_MODEL` when set; otherwise it defaults
to `llama3.2:latest`. Set `BPFCO_OLLAMA_MODEL=hermes3:8b` to give Fred Hermes
responses. The CEO planner also uses local Ollama when `BPFCO_OFFLINE=1`.

| Use | Model | Status |
| --- | --- | --- |
| Fred's substantial reasoning | `hermes3:8b` | Select with `BPFCO_OLLAMA_MODEL`; installed on the current laptop. |
| Quick routine replies on limited RAM | `llama3.2-lowvram:latest` | Installed on the current laptop; select explicitly. |
| Automatic routing by task complexity | Hermes for substantial work, low-VRAM model for quick work | Planned; **not implemented yet**. |

Do not add a larger local GPT model merely for its name. Evaluate it only when
hardware and download capacity can support it, using the same grounded task
set as Hermes. A hosted GPT API would require network access and separate API
usage; it cannot be the offline brain or a silent fallback for private files.

## Start the dashboard

Install the lightweight dashboard dependencies from `requirements.txt` or
install `Flask` and `python-dotenv` for dashboard-only use. Ollama and the
chosen model must already be installed. From the repository root, start
`ollama serve` in one shell. In a second PowerShell shell:

```powershell
$env:BPFCO_BOOT_MODE = 'offline'
$env:BPFCO_OFFLINE = '1'
$env:BPFCO_NETWORK_MODE = 'offline'
$env:BPFCO_ONLINE_INTELLIGENCE = '0'
$env:BPFCO_OLLAMA_MODEL = 'hermes3:8b'
py -3 .\ceo_dashboard.py
```

Open <http://127.0.0.1:5001/super>. Choose Fred and use **TASK FRED** to
record an internal objective and see the note paths used in his answer. The
specialist **QUEUE** action creates an internal task. `ceo_planner.py` can
queue the next planned task for each specialist. Check task and report records
under `Brain/Executive/` when diagnosing the queue.

For an explicit online session, set `BPFCO_BOOT_MODE=online`,
`BPFCO_OFFLINE=0`, `BPFCO_NETWORK_MODE=online`, and
`BPFCO_ONLINE_INTELLIGENCE=1` **before starting the dashboard**. OnlineGate
supports on-demand WorldMonitor research when configured. The current terminal
reply path still calls local Ollama; online research is not yet automatically
added to Fred's evidence. A configured cloud fallback in `omniroute.py` is a
separate capability and must not be mistaken for local reasoning.

`launch_app.py` runs more startup steps and opens desktop applications. Its
`Shared_Context/integrate_vault.py` step currently names
`C:\BPFCo\BPFCoBrain` directly, so check that path before using it from a
different worktree. Direct `ceo_dashboard.py` startup uses the current checkout.

## Architecture and next connections

| Component | Current responsibility |
| --- | --- |
| `agent_bridge.py` and `executive_controller.py` | Task records, queue, and specialist dispatch. |
| `agent_runtime.py` | Claim, report, and experience lifecycle. |
| `Brain/Executive/local_evidence.py` | Bounded local note retrieval with paths. |
| `omniroute.py` | Local model routing and optional cloud fallback. |
| `online_gate.py` | Optional, on-demand live intelligence. |
| `approval_gate.py` | Human approval before external execution. |
| `Dashboard/` and `ceo_dashboard.py` | Interface and local HTTP routes. |

Next: validate each specialist's queue-to-report path on the laptop, expose
the retrieved evidence alongside its report, add deliberate online intake
with timestamps and source attribution, and then implement measured
Hermes/low-VRAM routing. Preserve the existing queue, vault, and approval gate
while doing so.
## Fred graph and Meeting view

The Super dashboard at `/super` reads active task records through
`/api/meeting-tasks`. The Brain view at `/super-3d` reads
`/api/brain-graph`. The graph uses the existing vault index, executive
records, explicit local note links and exact task evidence or report source
paths. It does not create task records or alter documents.

To include a local document folder, set `BPFCO_DOCUMENTS_ROOT` to its existing
path before starting the dashboard. The bounded scanner reads supported
Markdown, text, DOCX and PDF files; it merges only verified byte-identical
copies. Each graph refresh extracts a limited batch, so the pending count can
fall over several refreshes. PDF text needs an already installed offline
extractor. Missing or ambiguous references remain unlinked. Network mode does
not control local document reading.

Check `/api/brain-graph` for `notes`, `executive_links`,
`provenance_links`, `document_pending` and
`document_unverified_hashes` before integrating a changed checkout. The
Meeting view shows queued and in-progress tasks from the existing queue and
task files.
## Automatic internal specialist queue

Starting `ceo_dashboard.py` directly on port 5001 binds the server first,
then runs one queued specialist at a time in a background thread. The terminal
`RUN NEXT` button remains available when Fred is selected. Both use the same
lock, so a manual request returns a busy response while a specialist runs.
The queue pauses on worker failure for review. Preview launchers that import
only the Flask app do not start automatic dispatch. The workers' existing
approval checks still govern external actions. Task and report records stay
under the existing Executive directories.
## Read-only live comparison

Use `scripts/run_fred_compare.py --live <running-checkout> --documents
<document-folder>` from an isolated worktree to display the merged dashboard
on port 5002 with the running checkout's index and Executive records. The
preview serves its own dashboard files, reads the existing documents in place,
blocks all HTTP write methods, disables automatic queue startup, and stays
on loopback. Stop it with Ctrl+C. Check graph statistics and Meeting tasks in
this preview before changing a desktop launcher or integrating dirty files.
The preview also records each document's real containing directory. Folder
edges describe file location only; `document_links` continues to count
explicit references in content. Duplicate aliases still point to one verified
content node. A crowded folder graph must not be mistaken for evidence that
those documents discuss one another.
## Offline Fred runtime backup

Run `scripts/backup_fred_runtime.py --live <checkout> --destination
<existing-offline-folder>` to create one ZIP archive outside the live checkout.
The archive contains `Brain/Executive` and `.vault-index.json`, including
uncommitted task and report records. It excludes source documents and the rest
of the vault. No running task or source file is changed.

The script streams files, rejects a changing source, writes a temporary ZIP,
extracts it into a temporary restore folder, checks every SHA-256 digest and
the restored index structure, removes that folder, and only then publishes the
final ZIP. The destination must already exist and have enough space for the
archive and restore check. This ZIP is unencrypted; keep it on trusted offline
storage. To preserve the original documents, back up their source folder
separately.
