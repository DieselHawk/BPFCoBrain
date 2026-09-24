# Fred versus Agno: bounded document task comparison

Date: 2026-09-24. All execution occurred in disposable Linux scratch directories. No live queue or Windows files were available. Agno 3.0.11 and SQLAlchemy were installed in a separate virtual environment. No Ollama model was invoked.

## Common input

Task: `Ingest the AllNew Docs for overview`.
Source set: two local fixture files in an unindexed `AllNew Docs` folder, plus one unrelated file. A previously indexed synthetic overview note was also present in Fred's scratch vault.

| Stage | Fred (isolated branch) | Agno 3.0.11 |
| --- | --- | --- |
| Folder discovery | With explicit `BPFCO_DOCUMENTS_ROOT`, Fred returned the two matching external files plus the indexed note; unrelated content was omitted. Previously, external unindexed files were invisible. | Agno's `SqliteDb` provides storage, not document discovery. A document reader/tool would still need to be configured; this stage was not run in Agno. |
| Task lifecycle | Dispatch → claim → report completed in scratch; source paths attached and external execution blocked. | No equivalent workflow configured or tested. |
| Duplicate memory | Fred's task-keyed experience writer kept one file per task. | Upserting the same `memory_id` twice kept one row. |
| Shared recall | Fred's completed experience was initially invisible to retrieval; this branch now retrieves recent experience files directly. | Reopening the same SQLite database returned the one memory for the same user ID. |
| Import cost in this Linux sandbox | Fred imports: 0.017 seconds, 9,344 KB peak RSS. | Agno SQLite imports: 0.537 seconds, 54,036 KB peak RSS. |

The import measurements are one-off sandbox observations, not a Windows RAM benchmark. Agno's immediate shared SQLite memory is useful, but the test does not establish better document ingestion or agent reasoning. Fred now has bounded local folder lookup and direct recall of recent experience files; both require validation against the real Windows folder and existing queue before merging.

Next required evidence: identify the actual AllNew Docs path, file types, and Fred task ID in the laptop checkout. Then run a read-only preview with that task ID and limit; do not claim or complete it during validation.
