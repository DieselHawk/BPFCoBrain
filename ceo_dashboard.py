import json
from pathlib import Path
from flask import Flask, jsonify, request, render_template_string, send_file
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
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

from Dashboard.agent_terminal_routes import agent_terminal_bp
app.register_blueprint(agent_terminal_bp)

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
        # Use a small retry loop for file locks
        for _ in range(3):
            try:
                return json.loads(path.read_text(encoding="utf-8-sig"))
            except IOError:
                import time
                time.sleep(0.01)
    except Exception:
        pass
    return default


@app.route("/")
def home():
    return render_template_string(HTML)


# LIVE_AGENT_STATE_V04
def live_agent_states():
    tasks = []
    try:
        for path in TASK_DIR.glob("*.json"):
            item = load_json(path, {})
            if item:
                tasks.append(item)
    except Exception:
        pass

    presence = load_json(
        EXECUTIVE_DIR / "presence_state.json",
        {}
    )

    states = {
        "Fred": {"state":"READY","task":None},
        "Bob": {"state":"READY","task":None},
        "Cindy": {"state":"READY","task":None},
        "Kai": {"state":"READY","task":None},
        "Neo": {"state":"READY","task":None},
    }

    name_map = {
        "Bob_Finance":"Bob",
        "Cindy_Secretary":"Cindy",
        "Kai_Legal":"Kai",
        "Neo_Sales":"Neo",
    }

    for task in tasks:
        agent = name_map.get(task.get("agent"))
        if not agent:
            continue

        status = task.get("status")
        if status == "in_progress":
            states[agent] = {
                "state":"WORKING",
                "task":{
                    "task_id":task.get("task_id"),
                    "objective":task.get("objective")
                }
            }
        elif status == "queued" and states[agent]["state"] == "READY":
            states[agent] = {
                "state":"QUEUED",
                "task":{
                    "task_id":task.get("task_id"),
                    "objective":task.get("objective")
                }
            }

    # Explicit speaking/listening presence wins. Active runtime work remains
    # authoritative so the avatar reflects QUEUED/WORKING task state.
    if (
        presence.get("agent") in states
        and (
            states[presence["agent"]]["state"] == "READY"
            or presence.get("state") in {"SPEAKING", "LISTENING", "THINKING"}
        )
    ):
        states[presence["agent"]] = {
            "state":presence.get("state","PRESENT"),
            "task":states[presence["agent"]].get("task")
        }

    return states
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
        "live_states": live_agent_states(),
    })


@app.route("/api/meeting-tasks")
def meeting_tasks():
    """Read existing task records for the Meeting view; never alter the queue."""
    queue_items = load_json(QUEUE_FILE, [])
    if not isinstance(queue_items, list):
        queue_items = []
    ordered = []
    seen = set()
    for item in queue_items:
        if isinstance(item, dict):
            task_id = str(item.get("task_id", ""))
            if task_id and task_id not in seen:
                ordered.append(task_id)
                seen.add(task_id)
    for path in sorted(TASK_DIR.glob("*.json")):
        task_id = path.stem
        if task_id in seen:
            continue
        record = load_json(path, {})
        if isinstance(record, dict) and record.get("status") in {"queued", "in_progress"}:
            ordered.append(task_id)
            seen.add(task_id)
    tasks = []
    for task_id in ordered:
        # IDs are generated by AgentBridge; ignore malformed queue entries.
        if not task_id or any(ch not in "0123456789TZ-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" for ch in task_id):
            continue
        record = load_json(TASK_DIR / (task_id + ".json"), {})
        if not isinstance(record, dict) or record.get("status") not in {"queued", "in_progress"}:
            continue
        tasks.append({
            "task_id": task_id,
            "agent": str(record.get("agent", "")),
            "status": str(record.get("status", "")),
            "objective": str(record.get("objective", ""))[:2000],
            "created_at": record.get("created_at", ""),
        })
    return jsonify({"tasks": tasks, "count": len(tasks)})


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



# SUPER_BRAIN_ROUTES
@app.route("/super")
def super_dashboard():
    dashboard_path = ROOT / "Dashboard" / "super_dashboard.html"
    # Mount the terminal on the canonical /super page.
    html = dashboard_path.read_text(encoding="utf-8-sig")
    html = html.replace(
        "</head>",
        '<link rel="stylesheet" href="/agent-terminal/terminal.css">\n</head>',
        1,
    )
    html = html.replace(
        "</body>",
        '<script src="/agent-terminal/terminal.js"></script>\n</body>',
        1,
    )
    return html

@app.route("/brain-graph")
def brain_graph():
    return send_file(ROOT / "dashboard.html")

@app.route("/.vault-index.json")
def vault_index():
    return send_file(ROOT / ".vault-index.json")

@app.route("/vendor/d3.v7.min.js")
def d3_asset():
    return send_file(ROOT / "Dashboard" / "vendor" / "d3.v7.min.js")

@app.route("/vendor/3d-force-graph.min.js")
def force_graph_3d_asset():
    return send_file(ROOT / "Dashboard" / "vendor" / "3d-force-graph.min.js")
# PRESENCE_V01 (Consolidated)
PRESENCE_FILE = EXECUTIVE_DIR / "presence_state.json"

@app.route("/api/presence", methods=["GET","POST"])
def presence():
    if request.method == "GET":
        return jsonify(load_json(PRESENCE_FILE, {
            "agent":"Fred",
            "state":"IDLE",
            "event":"none"
        }))

    data = request.get_json(silent=True) or {}
    agent = str(data.get("agent","Fred")).strip()
    state_name = str(data.get("state","PRESENT")).strip()
    event = str(data.get("event","call")).strip()

    allowed = {"Fred","Bob","Cindy","Kai","Neo"}
    if agent not in allowed:
        return jsonify({"ok":False,"error":"Unknown agent"}),400

    state = {
        "agent":agent,
        "state":state_name,
        "event":event
    }

    try:
        PRESENCE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as e:
        return jsonify({"ok":False,"error":f"File lock: {e}"}), 500
        
    return jsonify({"ok":True,"presence":state})
# PRESENCE_FRAME_API_V01
@app.route("/api/presence/frame")
def presence_frame():
    import json as _json
    from Presence.adapters.bpfco_presence_adapter import make_frame

    state_file = ROOT / "Brain" / "Executive" / "presence_state.json"

    if state_file.exists():
        try:
            raw = _json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            raw = {}
    else:
        raw = {}

    agent = raw.get("agent","Fred")
    runtime = live_agent_states().get(agent, {})
    state_name = runtime.get("state") or raw.get("state","IDLE")

    frame = make_frame(
        agent,
        state_name,
        raw.get("event","none")
    )

    return jsonify({
        "ok": True,
        "frame": frame.__dict__,
        "runtime": {
            "state": state_name,
            "task": runtime.get("task"),
            "connected": True,
        }
    })
# BPFCO_ACTIVITY_V01
def bpfco_activity():
    events=[]

    def add(ts,agent,event,detail):
        events.append({
            "time":ts,
            "agent":agent,
            "event":event,
            "detail":detail
        })

    presence_file = ROOT / "Brain" / "Executive" / "presence_state.json"
    if presence_file.exists():
        try:
            x=json.loads(presence_file.read_text(encoding="utf-8"))
            add(
                presence_file.stat().st_mtime,
                x.get("agent","Fred"),
                "PRESENCE",
                x.get("state","IDLE")+" · "+x.get("event","none")
            )
        except Exception:
            pass

    queue_file = ROOT / "Brain" / "Executive" / "queue.json"
    if queue_file.exists():
        try:
            q=json.loads(queue_file.read_text(encoding="utf-8"))
            items=q if isinstance(q,list) else (
                q.get("tasks",q.get("queue",[])) if isinstance(q,dict) else []
            )
            if isinstance(items,list):
                add(
                    queue_file.stat().st_mtime,
                    "Fred",
                    "QUEUE",
                    f"{len(items)} queued item(s)"
                )
        except Exception:
            add(queue_file.stat().st_mtime,"Fred","QUEUE","queue updated")

    task_dir = ROOT / "Brain" / "Executive" / "tasks"
    if task_dir.exists():
        for path in sorted(
            task_dir.glob("*.json"),
            key=lambda x:x.stat().st_mtime,
            reverse=True
        )[:12]:
            try:
                x=json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                x={}

            agent=x.get("agent",path.stem.split("-")[-1])
            status=x.get("status",x.get("state","TASK"))
            objective=x.get("objective",x.get("title","task"))
            add(path.stat().st_mtime,agent,"TASK",f"{status} · {objective}")

    roll = ROOT / "Brain" / "Executive" / "rollover"
    if roll.exists():
        for path in sorted(
            roll.glob("*.json"),
            key=lambda x:x.stat().st_mtime,
            reverse=True
        )[:5]:
            add(path.stat().st_mtime,"Fred","ROLLOVER",path.name)

    reports = ROOT / "Brain" / "Executive"
    for path in sorted(
        reports.rglob("*.md"),
        key=lambda x:x.stat().st_mtime,
        reverse=True
    )[:8]:
        if "Report" in path.name or "report" in path.name or "CEO_" in path.name:
            add(path.stat().st_mtime,"Fred","REPORT",path.name)

    return sorted(events,key=lambda x:x["time"],reverse=True)[:30]

@app.route("/api/activity")
def activity_api():
    return jsonify({"events":bpfco_activity()})
# BPFCO_BRAIN_GRAPH_API_V01
@app.route("/api/brain-graph")
def brain_graph_api():
    from Dashboard.adapters.brain_graph_adapter import build_brain_graph
    from Dashboard.adapters.provenance_edges import add_provenance_edges
    from Dashboard.adapters.note_edges import add_note_edges
    from Dashboard.adapters.document_edges import add_document_edges
    graph = add_note_edges(build_brain_graph(), ROOT)
    graph = add_document_edges(graph, ROOT)
    return jsonify(add_provenance_edges(graph, ROOT))

@app.route("/super-3d")
def super_brain_3d():
    return send_file(ROOT / "Dashboard" / "super_brain_3d.html")
if __name__ == "__main__":
    from boot_network import configure_environment
    print(f"[BPFCoBrain] Network mode: {configure_environment().upper()}")
    print("[BPFCoBrain] Starting CEO Executive Dashboard...")
    app.run(host="127.0.0.1", port=5001, debug=False)





