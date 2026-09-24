"""Compare a detached draft graph with the running CEO graph, without dispatching tasks."""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from Dashboard.adapters.brain_graph_adapter import build_brain_graph
from Dashboard.adapters.document_edges import add_document_edges
from Dashboard.adapters.note_edges import add_note_edges
from Dashboard.adapters.provenance_edges import add_provenance_edges
import Dashboard.adapters.brain_graph_adapter as adapter


def get_json(url):
    with urllib.request.urlopen(url, timeout=35) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("live", type=Path, help="Currently running checkout root")
    parser.add_argument("--url", default="http://127.0.0.1:5001")
    parser.add_argument("--documents", type=Path)
    args = parser.parse_args()
    live = args.live.resolve()
    index = live / ".vault-index.json"
    if not index.is_file():
        parser.error("Live checkout has no .vault-index.json")
    current = get_json(args.url.rstrip("/") + "/api/brain-graph")
    meeting = get_json(args.url.rstrip("/") + "/api/meeting-tasks")
    adapter.ROOT = live
    adapter.INDEX = index
    draft = add_note_edges(build_brain_graph(), live)
    documents = args.documents or os.environ.get("BPFCO_DOCUMENTS_ROOT")
    if documents:
        source = Path(documents).resolve()
        if not source.is_dir():
            parser.error("Document source unavailable")
        draft = add_document_edges(draft, live, source)
    else:
        print("Documents: skipped (pass --documents for full comparison)")
    draft = add_provenance_edges(draft, live)
    before, after = current.get("stats", {}), draft.get("stats", {})
    print("Current: " + json.dumps({key: before.get(key) for key in
          ("notes", "executive_links", "provenance_links", "resolved_links")}, sort_keys=True))
    print("Draft:   " + json.dumps({key: after.get(key) for key in
          ("notes", "executive_links", "provenance_links", "resolved_links",
           "document_sources", "document_pending", "document_unverified_hashes",
           "source_files_seen", "source_snapshot")}, sort_keys=True))
    print("Meeting endpoint: " + ("OK" if isinstance(meeting, (list, dict)) else "INVALID"))
    failures = []
    if after.get("notes") != before.get("notes"):
        failures.append("note count changed")
    if after.get("executive_links") != before.get("executive_links"):
        failures.append("executive connections differ on the same records")
    if not isinstance(meeting, (list, dict)):
        failures.append("meeting tasks response invalid")
    if after.get("provenance_links", 0) < 1:
        failures.append("no file provenance links resolved")
    if documents and after.get("document_unverified_hashes", 0):
        failures.append("some document hashes could not be verified")
    if failures:
        print("CHECK FAILED: " + "; ".join(failures))
        return 1
    print("GRAPH COMPARISON PASSED (read-only; no tasks dispatched)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, urllib.error.URLError, ValueError, json.JSONDecodeError) as exc:
        print("CHECK STOPPED: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
