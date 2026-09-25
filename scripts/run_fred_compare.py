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
    parser.add_argument("--port", type=int, default=5002)
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
    os.environ["BPFCO_PREVIEW_READ_ONLY"] = "1"
    os.environ["BPFCO_DOCUMENTS_ROOT"] = str(documents)

    from flask import abort, jsonify, request
    from werkzeug.serving import make_server
    import ceo_dashboard as dashboard
    from Dashboard.adapters import brain_graph_adapter as adapter
    from Dashboard.adapters.note_edges import add_note_edges
    from Dashboard.adapters.document_edges import add_document_edges
    from Dashboard.adapters.provenance_edges import add_provenance_edges
    from Dashboard.adapters.source_edges import add_source_edges
    from Brain.Executive import local_evidence

    executive = live / "Brain" / "Executive"
    dashboard.EXECUTIVE_DIR = executive
    dashboard.TASK_DIR = executive / "tasks"
    dashboard.REPORT_DIR = executive / "reports"
    dashboard.QUEUE_FILE = executive / "queue.json"
    dashboard.STATE_FILE = executive / "state.json"
    dashboard.PLAN_FILE = executive / "CEO_Work_Plan.md"
    dashboard.MORNING_FILE = executive / "CEO_Morning_Report.md"
    dashboard.GRAPHIFY_ROOT = live
    adapter.ROOT = live
    adapter.INDEX = live / ".vault-index.json"
    local_evidence.ROOT = live
    local_evidence.INDEX = live / ".vault-index.json"

    def live_graph():
        graph = add_note_edges(adapter.build_brain_graph(), live)
        graph = add_document_edges(graph, live, documents)
        graph = add_source_edges(graph, live)
        return jsonify(add_provenance_edges(graph, live))

    dashboard.app.view_functions["brain_graph_api"] = live_graph

    @dashboard.app.get("/api/evidence-preview")
    def evidence_preview():
        objective = request.args.get("objective", "").strip()
        if not objective or len(objective) > 400:
            return jsonify({"error": "Objective must be 1-400 characters"}), 400
        evidence = local_evidence.retrieve(objective, limit=8)
        return jsonify({"evidence": evidence, "count": len(evidence)})

    @dashboard.app.before_request
    def preview_read_only():
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            abort(405)

    # Binding first prevents the preview from running on an occupied port.
    if not 1024 <= args.port <= 65535:
        parser.error("Choose an unprivileged TCP port")
    server = make_server("127.0.0.1", args.port, dashboard.app, threaded=True)
    from Brain.Executive.action_journal import record as audit_record
    audit_record("dashboard_started", mode="preview_read_only", port=args.port,
                 checkout=str(ROOT), live_source=str(live))
    url = f"http://127.0.0.1:{args.port}/super"
    print("Fred comparison: read-only; automatic queue disabled", flush=True)
    print("Live vault and records: " + str(live), flush=True)
    print("Document source: " + str(documents), flush=True)
    print("Open " + url, flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    finally:
        audit_record("dashboard_stopped", mode="preview_read_only", port=args.port)
        server.server_close()


if __name__ == "__main__":
    main()
