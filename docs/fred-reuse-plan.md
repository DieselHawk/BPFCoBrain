# Reuse plan for Fred

Keep Fred's queue, reports, Super dashboard, vault, and approval gate as the contract. Test one external component at a time in an isolated checkout; do not migrate live state or install an entire agent suite.

| Need | Existing implementation | Reusable component | Trial boundary |
| --- | --- | --- | --- |
| Shared searchable memory | `Brain/Executive/Experience/`, `.vault-index.json`, `local_evidence.py` | Agno `SqliteDb` shared-memory pattern, or Python standard-library `sqlite3` if the dependency footprint is too large | Build a separate index from copies of three notes; verify deduplication and agent visibility before migration. |
| Durable task checkpoints | `agent_bridge.py`, `queue.json`, `approval_gate.py` | LangGraph SQLite checkpointer and interrupt pattern | Prototype a single claim → report → approval task using a disposable DB; retain current queue until parity is proven. |
| Gmail intake | `google_auth.py`, `gmail_hunt.py` | Google's maintained Gmail API Python client and OAuth refresh | Read-only metadata test, no bulk copying, no sending. |
| OneDrive intake | `ondrive_hunt.py` | MSAL Python persistent token cache with delegated device login; Graph API | Fix token refresh and search in isolation; list a small page of file metadata before opening content. |
| Backups | `backup_fred.py` state archive | restic Windows snapshots and deduplication | Test a separate destination and restore into an empty directory; never place the repository inside its own source tree. |

Source material:
- https://docs.agno.com/memory/agent/agents-share-memory
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://developers.google.com/workspace/gmail/api/quickstart/python
- https://learn.microsoft.com/en-us/entra/msal/python/advanced/msal-python-token-cache-serialization
- https://restic.readthedocs.io/en/stable/040_backup.html

Decisions before any live ingestion:
1. Keep one canonical vault path resolved from the checkout; no second Brain folder.
2. Store pointers, hashes and source timestamps for external content first, then retrieve bounded excerpts on demand.
3. Keep OAuth secrets outside the vault index and Git; do not include them in an unencrypted archive.
4. Run agents sequentially on the 4 GB laptop. Online readers return evidence; they never authorize sends.
5. Benchmark peak RAM and a restore test before replacing any component.

## Dependency and network rules

No added dependency is required for the Fred folder lookup or network toggle.
The Agno trial lives outside the checkout and does not change
`requirements.txt`. Sandbox metadata identified Agno 3.0.11 as Apache 2.0,
SQLAlchemy 2.0.54 as MIT, and Flask 3.1.3 as BSD 3-Clause. Before any laptop
installation, validate the complete dependency tree and keep Windows wheels
locally so the same setup works without network access.

The Super dashboard terminal has an ONLINE/OFFLINE button. Switching saves
`Brain/Executive/network_mode.json` locally and updates the dashboard
process. Existing separate worker processes need a restart to inherit it.
An explicit `BPFCO_BOOT_MODE=online` or `offline` at startup overrides
the saved preference; `auto` uses the saved preference first. Offline
sets `BPFCO_OFFLINE=1` and disables the online intelligence gate.

## Agent autonomy and graph provenance

Kai and the other specialists may research, discuss, draft, challenge each
other, and record internal experiences without an approval step. The existing
human gate continues to govern sends, filings, publication, payments, and
other external execution.

The Brain API now adds edges from each task's existing `evidence[].path` and
each report's `sources[]` to a matching indexed note node. It reads records
without changing them, requires an exact path match, and ignores unmatched
paths. These are evidence provenance links, not newly inferred note-to-note
wikilinks. They are added only when the graph adapter already exposes task,
report, and note nodes with paths.
