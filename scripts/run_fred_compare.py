"""Serve merged UI with live records on port 5002 without running tasks."""
import argparse
import os
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", required=True, type=Path)
    parser.add_argument("--documents", required=True, type=Path)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    live = args.live.resolve()
    documents = args.documents.resolve()
    if live == ROOT or not (live / ".vault-index.json").is_file():
        parser.error("Choose the separate live checkout with its existing vault index")
    if not documents.is_dir():
        parser.error("Document source unavailable")

    # An imported dashboard never runs its __main__ queue worker. Keep this
    # preview offline and block HTTP writes as a second safeguard.
    os.environ["BPFCO_OFFLINE"] = "1"
    os.environ["BPFCO_ONLINE_INTELLIGENCE"] = "0"
    os.environ["BPFCO_CLOUD_FALLBACK"] = "0"
    os.environ["BPFCO_DOCUMENTS_ROOT"] = str(documents)

    from flask import abort, jsonify, request
    from werkzeug.serving import make_server
    import ceo_dashboard as dashboard
    from Dashboard.adapters import brain_graph_adapter as adapter
    from Dashboard.adapters.note_edges import add_note_edges
    from Dashboard.adapters.document_edges import add_document_edges
    from Dashboard.adapters.provenance_edges import add_provenance_edges

    executive = live / "Brain" / "Executive"
    dashboard.EXECUTIVE_DIR = executive
    dashboard.TASK_DIR = executive / "tasks"
    dashboard.REPORT_DIR = executive / "reports"
    dashboard.QUEUE_FILE = executive / "queue.json"
    dashboard.STATE_FILE = executive / "state.json"
    dashboard.PLAN_FILE = executive / "CEO_Work_Plan.md"
    dashboard.MORNING_FILE = executive / "CEO_Morning_Report.md"
    adapter.ROOT = live
    adapter.INDEX = live / ".vault-index.json"

    def live_graph():
        graph = add_note_edges(adapter.build_brain_graph(), live)
        graph = add_document_edges(graph, live, documents)
        return jsonify(add_provenance_edges(graph, live))

    dashboard.app.view_functions["brain_graph_api"] = live_graph

    @dashboard.app.before_request
    def preview_read_only():
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            abort(405)

    # Binding first prevents the preview from running on an occupied port.
    server = make_server("127.0.0.1", 5002, dashboard.app, threaded=True)
    url = "http://127.0.0.1:5002/super"
    print("Fred comparison: read-only; automatic queue disabled", flush=True)
    print("Live vault and records: " + str(live), flush=True)
    print("Document source: " + str(documents), flush=True)
    print("Open " + url, flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
