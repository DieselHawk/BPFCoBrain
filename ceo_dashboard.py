import json
from pathlib import Path
from flask import Flask, jsonify, request, render_template_string

ROOT = Path(r"C:\BPFCo\BPFCoBrain")
EXECUTIVE_DIR = ROOT / "Brain" / "Executive"
TASK_DIR = EXECUTIVE_DIR / "tasks"
REPORT_DIR = EXECUTIVE_DIR / "reports"
QUEUE_FILE = EXECUTIVE_DIR / "queue.json"
STATE_FILE = EXECUTIVE_DIR / "state.json"
PLAN_FILE = EXECUTIVE_DIR / "CEO_Work_Plan.md"
MORNING_FILE = EXECUTIVE_DIR / "CEO_Morning_Report.md"

from agent_bridge import AgentBridge

app = Flask(__name__)
bridge = AgentBridge()

AGENTS = {
    "Bob_Finance": "Finance, accounting and billing",
    "Cindy_Secretary": "Secretary and administration",
    "Kai_Legal": "Legal research, case management and drafting",
    "Neo_Sales": "Marketing, sales, lead generation and campaigns",
}

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>BPFCoBrain CEO</title>
<style>
body{font-family:Arial,sans-serif;background:#111;color:#eee;margin:0}
header{padding:20px;background:#1d1d1d;border-bottom:1px solid #444}
h1{margin:0 0 5px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:15px;padding:20px}
.card{background:#1b1b1b;border:1px solid #444;border-radius:8px;padding:15px}
.agent{padding:10px;margin:8px 0;background:#222;border-radius:6px}
.ok{color:#59e391}.warn{color:#ffd166}
button{padding:9px 14px;border:0;border-radius:5px;cursor:pointer}
input,select,textarea{width:100%;box-sizing:border-box;margin:6px 0;padding:9px;background:#222;color:#fff;border:1px solid #555;border-radius:4px}
textarea{min-height:90px}
pre{white-space:pre-wrap;max-height:350px;overflow:auto}
.small{font-size:12px;color:#aaa}
</style>
</head>
<body>
<header>
<h1>BPFCoBrain - CEO Executive Control</h1>
<div class="small">Local executive interface - external execution remains approval-gated</div>
</header>

<div class="grid">

<div class="card">
<h2>System</h2>
<div id="system">Loading...</div>
<button onclick="refreshAll()">Refresh</button>
</div>

<div class="card">
<h2>Agents</h2>
<div id="agents">Loading...</div>
</div>

<div class="card">
<h2>Dispatch Task</h2>
<select id="agent">
<option value="Bob_Finance">Bob - Finance</option>
<option value="Cindy_Secretary">Cindy - Secretary</option>
<option value="Kai_Legal">Kai - Legal</option>
<option value="Neo_Sales">Neo - Sales</option>
</select>
<input id="priority" value="normal" placeholder="Priority">
<textarea id="objective" placeholder="What should the agent work on?"></textarea>
<button onclick="dispatchTask()">Send to agent</button>
<pre id="dispatchResult"></pre>
</div>

<div class="card">
<h2>Queue</h2>
<pre id="queue">Loading...</pre>
</div>

<div class="card">
<h2>Agent Reports</h2>
<pre id="reports">Loading...</pre>
</div>

<div class="card">
<h2>CEO Work Plan</h2>
<pre id="plan">Loading...</pre>
</div>

<div class="card">
<h2>Approval Gate</h2>
<div class="warn">
External sends, payments, legal filings, contracts, publication and other
high-impact external actions remain blocked until the user approves them.
</div>
</div>

</div>

<script>
async function getJSON(url, options={}) {
    const r = await fetch(url, options);
    return await r.json();
}

async function refreshAll() {
    const data = await getJSON('/api/status');
    document.getElementById('system').innerHTML =
        '<div class="ok">CEO Controller: ' + (data.controller || 'unknown') + '</div>' +
        '<div>Persistent memory: ' + data.persistent_memory + '</div>' +
        '<div>Human approval: ' + data.human_approval + '</div>' +
        '<div>Queued tasks: ' + data.queued_tasks + '</div>' +
        '<div>Reports: ' + data.reports + '</div>';

    document.getElementById('agents').innerHTML =
        Object.entries(data.agents).map(([name,a]) =>
            '<div class="agent"><b>' + name + '</b><br>' +
            a.role + '<br>' +
            '<span class="' + (a.registered ? 'ok' : 'warn') + '">' +
            'registered=' + a.registered + '</span> - workspace_files=' + a.workspace_files +
            '</div>'
        ).join('');

    const q = await getJSON('/api/queue');
    document.getElementById('queue').textContent = JSON.stringify(q, null, 2);

    const reports = await getJSON('/api/reports');
    document.getElementById('reports').textContent = JSON.stringify(reports, null, 2);

    const plan = await getJSON('/api/plan');
    document.getElementById('plan').textContent = plan.content;
}

async function dispatchTask() {
    const payload = {
        agent: document.getElementById('agent').value,
        objective: document.getElementById('objective').value,
        priority: document.getElementById('priority').value || 'normal'
    };

    const result = await getJSON('/api/dispatch', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
    });

    document.getElementById('dispatchResult').textContent =
        JSON.stringify(result, null, 2);

    if (result.ok) {
        document.getElementById('objective').value = '';
        refreshAll();
    }
}

refreshAll();
setInterval(refreshAll, 15000);
</script>
</body>
</html>
"""


def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/api/status")
def status():
    state = load_json(STATE_FILE, {})
    queue = load_json(QUEUE_FILE, [])
    reports = []
    for path in sorted(REPORT_DIR.glob("*.json")):
        data = load_json(path, {})
        if data:
            reports.append(data)

    agents = {}
    for name, role in AGENTS.items():
        context_agents = load_json(EXECUTIVE_DIR / "shared_context.json", {}).get("agents", {})
        agents[name] = {
            "registered": bool(state.get("agents", {}).get(name, {}).get("registered", False)),
            "workspace_files": len(context_agents.get(name, {}).get("files", [])),
            "role": role,
        }

    return jsonify({
        "controller": state.get("controller", "CEO"),
        "persistent_memory": state.get("persistent_memory", False),
        "human_approval": state.get("human_approval_file", False),
        "queued_tasks": len(queue),
        "reports": len(reports),
        "agents": agents,
    })


@app.route("/api/queue")
def queue():
    return jsonify(load_json(QUEUE_FILE, []))


@app.route("/api/reports")
def reports():
    result = []
    for path in sorted(REPORT_DIR.glob("*.json")):
        data = load_json(path, {})
        if data:
            result.append(data)
    return jsonify(result[-20:])


@app.route("/api/plan")
def plan():
    content = PLAN_FILE.read_text(encoding="utf-8") if PLAN_FILE.exists() else "No CEO work plan yet."
    return jsonify({"content": content})


@app.route("/api/dispatch", methods=["POST"])
def dispatch():
    data = request.get_json(silent=True) or {}
    agent = data.get("agent", "")
    objective = str(data.get("objective", "")).strip()
    priority = str(data.get("priority", "normal")).strip() or "normal"

    if agent not in AGENTS:
        return jsonify({"ok": False, "error": "Unknown agent"}), 400
    if not objective:
        return jsonify({"ok": False, "error": "Objective is required"}), 400

    task = bridge.dispatch(
        agent,
        objective,
        priority=priority,
        approval_required=True,
    )

    return jsonify({
        "ok": True,
        "task": task,
        "message": "Task queued for the specialist. External execution remains blocked."
    })


if __name__ == "__main__":
    print("[BPFCoBrain] Starting CEO Executive Dashboard...")
    app.run(host="127.0.0.1", port=5001, debug=False)


