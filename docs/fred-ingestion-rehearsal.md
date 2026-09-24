# Fred bounded ingestion rehearsal — 2026-09-24

Scope: isolated scratch checkout containing copied `agent_bridge.py`, `local_evidence.py`, `experience_synthesizer.py`, and `backup_fred.py` from this branch. Used a synthetic `AllNew_Docs/overview.md` indexed in a disposable `.vault-index.json`. No live queue, mail account, OneDrive, Windows document folder, Ollama model, or agent worker was touched.

| Stage | Observed result |
| --- | --- |
| Dispatch and retrieve | Task created with one bounded evidence excerpt and `internal_only` mode. |
| Duplicate dispatch | Same task returned; queue stayed at one item. |
| Claim | Task moved to `in_progress`. |
| Experience write | One task-keyed file; a repeated write returned the same file without replacing content. |
| Report handoff | Report carried source path; queue became empty; external execution remained blocked pending approval. |
| Backup | Archive contained seven disposable state files; ZIP integrity verification passed. |

The representative task was completed **only inside the disposable test**. This establishes behavior of these stages, not actual ingestion of AllNew Docs. The real task and folder were absent from the repository snapshot. Current retrieval only reads paths already present in `.vault-index.json`; new external folders need a controlled index step. Agno, MSAL and restic were not installed or tested in this rehearsal.
