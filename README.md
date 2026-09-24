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
| Quick routine replies on limited RAM | `llama3.2:latest` | Select explicitly; verify it is installed with `ollama list`. |
| Automatic routing by task complexity | Hermes for substantial work, a smaller installed model for quick work | Planned; **not implemented yet**. |

Do not add a larger local GPT model merely for its name. Evaluate it only when
hardware and download capacity can support it, using the same grounded task
set as Hermes. A hosted GPT API would require network access and separate API
usage; it cannot be the offline brain or a silent fallback for private files.

## Start the dashboard

Install the free, open-source dependencies from `requirements.txt` or
install `Flask` and `python-dotenv` for dashboard-only use. Ollama and the
chosen model must already be installed. From the repository root, start
`ollama serve` in one shell. In a second PowerShell shell:

```powershell
$env:BPFCO_BOOT_MODE = 'offline'
$env:BPFCO_OLLAMA_MODEL = 'llama3.2:latest'
py -3 .\ceo_dashboard.py
```

Open <http://127.0.0.1:5001/super>. Choose Fred and use **TASK FRED** to
record an internal objective and see the note paths used in his answer. The
specialist **QUEUE** action creates an internal task. `ceo_planner.py` can
queue the next planned task for each specialist. Check task and report records
under `Brain/Executive/` when diagnosing the queue.

The Fred terminal has an online/offline switch that saves its preference for
later launches. An explicit `BPFCO_BOOT_MODE` setting overrides that preference
at startup. Restart existing workers after changing modes so they inherit the
same environment. Offline and online terminal replies use local Ollama; the CEO
planner uses Ollama while offline and its existing deterministic path while
online. Leave `BPFCO_CLOUD_FALLBACK` unset: allowing network access alone does
not authorize hosted model calls. OnlineGate's on-demand research is separate;
live results are not yet automatically supplied as Fred's task evidence.

For the isolated preview, launch from `C:\BPFCo\FredPreview` with
`$env:BPFCO_BOOT_MODE = 'online'` and `py -3 .\ceo_dashboard.py`.
Open <http://127.0.0.1:5002/super> only if the preview process was started
on port 5002; direct startup defaults to port 5001. Always check the process
and port before comparing preview and main.

## Architecture and next connections

| Component | Current responsibility |
| --- | --- |
| `agent_bridge.py` and `executive_controller.py` | Task records, queue, and specialist dispatch. |
| `agent_runtime.py` | Claim, report, and experience lifecycle. |
| `Brain/Executive/local_evidence.py` | Bounded local note retrieval with paths. |
| `omniroute.py` | Local model routing; hosted fallback requires separate explicit opt-in and is disabled for this build. |
| `online_gate.py` and `online_requests.py` | Gated research and a locally recorded request lifecycle; live fetching is not yet wired into the terminal evidence path. |
| `approval_gate.py` | Human approval before external execution. |
| `Dashboard/` and `ceo_dashboard.py` | Interface, Meeting tasks, graph, and local HTTP routes. |

Next: validate each specialist's queue-to-report path on the laptop, expose
the retrieved evidence alongside its report, add deliberate online intake
with timestamps and source attribution, and then implement measured
Hermes/smaller-model routing. Preserve the existing queue, vault, and approval gate
while doing so.

## Fred's shared memory and online sources

The active checkout is the canonical vault. Fred and the specialist workers use
`Brain/Executive/` for the queue, reports and shared experiences; experience
records live in `Brain/Executive/Experience/`. Do not copy a second Brain
folder into this directory. `Shared_Context/integrate_vault.py` resolves its
path from the checkout being launched.

For online startup in PowerShell, from the intended checkout:

```powershell
$env:BPFCO_BOOT_MODE = 'online'
$env:BPFCO_OLLAMA_MODEL = 'llama3.2:latest'
py -3 .\launch_app.py
```

This enables the network gate; it does **not** authenticate Gmail or OneDrive,
automatically ingest either account, or grant Fred live access to them.
`gmail_hunt.py` requires a Google Desktop OAuth `credentials.json` and
`token.json`. `ondrive_hunt.py` requires an Azure app client ID and a valid
Microsoft login; its existing token implementation needs a refresh and search
repair before relying on it. Keep OAuth tokens outside commits. For a bounded, read-only local source, set
`BPFCO_DOCUMENTS_ROOT` to the desired folder before startup. The retriever
visits at most 200 entries and three subfolder levels, and reads only Markdown
or text files smaller than 1 MB. It keeps source paths and short excerpts; it
does not copy files into the vault. This retriever does not ingest PDF or DOCX. The separate preview graph can inspect them locally for explicit links. Outbound actions remain subject to the approval gate.

For an executive runtime state archive (queue, reports, experiences,
shared context and index), choose a destination outside the checkout, ideally
another drive:

```powershell
py -3 .\backup_fred.py 'D:\BPFCoBackups'
```

This archive covers executive state, shared context, and the index, not every
vault note or external document. Its restore has not yet been verified on
Windows, and the ZIP is not encrypted. Keep sensitive archives in an
access-controlled destination, keep a separate backup of source documents,
and test a restore before treating this as recovery-ready. Avoid placing
archives inside any indexed or synced Brain directory.

## Live Brain graph in the draft preview

The `/api/brain-graph` endpoint can scan up to 1,500 indexed Markdown files,
2 MB per note and 150 explicit links per note. It resolves local wikilinks and
Markdown links only when a destination is unique; ambiguous and missing targets
are not invented as connections. Source files are read only; their modification
times cache extracted links between requests. This scan supplements existing
index, task, report and experience links. The API reports `scanned_note_links`,
`ambiguous_note_links` and `notes_scanned` for inspection.

Set `BPFCO_DOCUMENTS_ROOT` to the actual folder in the preview process.
The graph inventories up to 1,000 Markdown, text, DOCX and PDF files (100 MB
per file, five subfolder levels) without copying their content into the vault.
Only an explicit link inside a document or an exact task/report source path
creates a connection. Identical files share one node with all source paths
retained as aliases; other files remain distinct. Hash verification is bounded
to 300 MB per request and continues on later refreshes. The API reports
duplicate and pending counts, which must be checked against the source
inventory. DOCX text uses Python's standard library. PDF extraction uses an
already installed offline `pdftotext` or `pypdf` if available; otherwise PDF
nodes remain unlinked unless a task/report cites their path. Text extraction
is capped at eight documents per refresh. No new dependency is installed.

The Windows preview script checks the 855-note index and inventories the
source before changing files. The user observed 780 source files and nine
SHA-256-identical groups containing 27 files; this count covers all file
types, while graph duplicate statistics cover only supported graph files.
The script and real document graph still need a Windows run before merging.

The `/super-3d` view refreshes the API every 15 seconds while visible and
keeps positions for unchanged nodes. It displays the 350 most connected nodes
and only real recorded edges; a new edge pulses briefly when first observed.
Those pulses indicate new graph data, **not agent thought or live network
traffic**. Further traffic visualization needs timestamped runtime events.
The bounded scan and browser script passed isolated fixture and syntax checks;
run it against the real preview vault and measure counts and latency before
merging. The preview's local executive adapter remains a separate merge blocker.

## Isolated preview checks and merge gate

As observed in the isolated preview on 24 September 2026, the graph had 855
indexed notes, 66 executive links and 101 additional provenance links (167
resolved links total). These figures depend on the copied runtime task/report
records and a locally modified `Dashboard/adapters/brain_graph_adapter.py`
from the layering checkout; they are **not** reproducible from this draft
branch alone. The note index still reports zero indexed connections and seven
unresolved note links, which need separate investigation. The graph renderer
uses live link degree so the extra connections are visible. Meeting mode lists
active tasks while omitting completed ones.

Experience notes with an explicit task ID can also link to existing task and report nodes. An isolated AllNew Docs check added those two links without duplicates; the draft branch still lacks the local executive graph adapter that supplies those nodes in the preview. The compressed sandbox includes a merge comparison report, but it is a synthetic fixture rather than a full integration test.

The online research request lifecycle was exercised with a simulated fetch,
not a live Gmail, OneDrive, or public-web ingestion. Confirm live source
behavior, visibility of agent requests, and the offline switch before calling
it integrated. Test the Windows backup restore and the local graph adapter
against the active checkout before merging.

This branch is a draft preview. Follow `AGENTS.md` and compare changes with
the current running checkout, its uncommitted edits, callers, and failure paths.
Keep the dirty layering and overlay checkouts intact; resolve differences
deliberately and only then consider a merge.
