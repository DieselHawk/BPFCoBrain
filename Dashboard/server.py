from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,subprocess,urllib.request

ROOT=Path(__file__).resolve().parents[1]
PORT=47900
INDEX=ROOT/".vault-index.json"

def walk(obj):
    yield obj
    if isinstance(obj,dict):
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj,list):
        for v in obj:
            yield from walk(v)

def first_key(data,key):
    for x in walk(data):
        if isinstance(x,dict) and key in x:
            return x[key]
    return None

def index_data():
    if not INDEX.exists():
        return {"notes":0,"words":0,"connections":0,"unresolved":0,"edges":[],"nodes":[]}

    try:
        data=json.loads(INDEX.read_text(encoding="utf-8"))
    except Exception:
        return {"notes":0,"words":0,"connections":0,"unresolved":0,"edges":[],"nodes":[]}

    notes=first_key(data,"total_notes") or first_key(data,"notes_count") or 0
    words=first_key(data,"total_words") or first_key(data,"word_count") or 0
    unresolved=first_key(data,"unresolved_links") or first_key(data,"unresolved") or 0
    raw=first_key(data,"connections")

    edges=[]
    if isinstance(raw,list):
        for e in raw:
            if isinstance(e,dict):
                a=e.get("source") or e.get("from") or e.get("from_note") or e.get("source_path")
                b=e.get("target") or e.get("to") or e.get("to_note") or e.get("target_path")
                if a and b: edges.append({"source":Path(str(a)).stem,"target":Path(str(b)).stem})
            elif isinstance(e,(list,tuple)) and len(e)>=2:
                edges.append({"source":Path(str(e[0])).stem,"target":Path(str(e[1])).stem})
        connections=len(edges)
    elif isinstance(raw,(int,float)):
        connections=int(raw)
    else:
        alt=first_key(data,"edges") or first_key(data,"relationships") or first_key(data,"links")
        if isinstance(alt,list):
            for e in alt:
                if isinstance(e,dict):
                    a=e.get("source") or e.get("from") or e.get("from_note")
                    b=e.get("target") or e.get("to") or e.get("to_note")
                    if a and b: edges.append({"source":Path(str(a)).stem,"target":Path(str(b)).stem})
            connections=len(edges)

    nodes=[]
    notes_dict=first_key(data,"notes")
    if isinstance(notes_dict,dict):
        nodes=list(notes_dict.keys())
    elif isinstance(notes_dict,list):
        for n in notes_dict:
            if isinstance(n,dict):
                p=n.get("path") or n.get("file") or n.get("source") or n.get("title")
                if p: nodes.append(Path(str(p)).stem)
            elif isinstance(n,str):
                nodes.append(Path(n).stem)
    nodes=list(dict.fromkeys(nodes))

    edges=[]
    if isinstance(notes_dict,dict):
        for src_id,info in notes_dict.items():
            if isinstance(info,dict):
                links=info.get("links")
                if isinstance(links,list):
                    for target in links:
                        edges.append({"source":src_id,"target":target})
    elif isinstance(raw,list):
        for e in raw:
            if isinstance(e,dict):
                a=e.get("source") or e.get("from") or e.get("from_note") or e.get("source_path")
                b=e.get("target") or e.get("to") or e.get("to_note") or e.get("target_path")
                if a and b: edges.append({"source":Path(str(a)).stem,"target":Path(str(b)).stem})
            elif isinstance(e,(list,tuple)) and len(e)>=2:
                edges.append({"source":Path(str(e[0])).stem,"target":Path(str(e[1])).stem})
    
    return {
        "notes":int(notes) if str(notes).isdigit() else len(nodes),
        "words":int(words) if str(words).isdigit() else 0,
        "connections":connections,
        "unresolved":int(unresolved) if str(unresolved).isdigit() else 0,
        "edges":edges[:700],
        "nodes":nodes[:250],
        "source":str(INDEX.relative_to(ROOT)).replace("\\","/")
    }
    def exists(p): return (ROOT/p).exists()
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags",timeout=1)
        ollama="ONLINE"
    except Exception:
        ollama="OFFLINE"
    try:
        git=subprocess.check_output(["git","status","--short"],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip() or "CLEAN"
    except Exception:
        git="UNKNOWN"
    return {
        "Git":git,
        "Ollama":ollama,
        "Agent Runtime":"READY" if exists("agent_runtime.py") else "MISSING",
        "OmniRoute":"READY" if exists("omniroute.py") else "MISSING",
        "Approval Gate":"READY" if exists("approval_gate.py") else "MISSING",
        "Vault Index":"READY" if INDEX.exists() else "MISSING"
    }

def payload():
    return {
        "agents":[
            ["fred","Fred","CEO"],["bob","Bob","Finance"],
            ["cindy","Cindy","Secretary"],["kai","Kai","Legal"],["neo","Neo","Sales"]],
        "knowledge":index_data(),
        "system":system()
    }

HTML=r'''<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>BPFCo Command Center</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#090d12;color:#eaf0f5;font:14px Segoe UI,Arial}
header{padding:20px 26px;border-bottom:1px solid #27333e;display:flex;justify-content:space-between}
h1{margin:3px 0;font-size:27px}.ey{font-size:10px;letter-spacing:.2em;color:#82909d}.muted{color:#82909d;font-size:12px}
.wrap{max-width:1450px;margin:auto;padding:16px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.panel{background:#10171f;border:1px solid #27343f;border-radius:13px;padding:15px}
.cards{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.card{padding:11px;border:1px solid #2b3945;border-radius:10px;background:#0d141b;text-align:center}.face{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;margin:auto auto 7px;background:#213441;font-weight:800}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.stat{padding:12px;border:1px solid #283540;border-radius:10px;background:#0d141b}.stat b{display:block;font-size:21px;margin-top:3px}.ok{color:#67dc98}.warn{color:#efbf65}
#graph{height:470px;border-radius:10px;background:radial-gradient(circle,#172733,#0b1117 67%);overflow:hidden}svg{width:100%;height:100%}.edge{stroke:#48606e;stroke-width:1.4;opacity:.55}.agentEdge{stroke:#63b9df;stroke-width:2}.node{fill:#16212a;stroke:#526674}.agentNode{fill:#193141;stroke:#6fc5ef}.nt{fill:#dce6ed;font-size:10px;text-anchor:middle}.label{fill:#92a1ad;font-size:9px}
.row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #202a34}.row:last-child{border:0}
@media(max-width:950px){.grid{grid-template-columns:1fr}.cards{grid-template-columns:repeat(2,1fr)}.stats{grid-template-columns:1fr 1fr}}
</style></head><body>
<header><div><div class=ey>BPFCo · BRAIN-DIRECT</div><h1>COMMAND CENTER</h1><div class=muted>Dashboard consumes BPFCoBrain data — it does not recreate it.</div></div><div class=muted><span class=ok>LOCAL</span> · <span id=t>--:--:--</span></div></header>
<main class=wrap>
<section class=panel><div class=ey>AGENT FLEET</div><div class=cards id=a style="margin-top:10px"></div></section>

<div class=grid style="margin-top:14px">
<section class=panel><div class=ey>BPFCoBRAIN KNOWLEDGE DATA</div><div class=stats style="margin-top:10px" id=k></div><div class=muted style="margin-top:10px" id=source></div></section>
<section class=panel><div class=ey>CORE STATUS</div><div id=s style="margin-top:8px"></div></section>
</div>

<section class=panel style="margin-top:14px"><div class=ey>KNOWLEDGE CONNECTION MAP</div><div class=muted style="margin:5px 0 10px">Connections shown here come from the BPFCoBrain index/relationship data.</div><div id=graph></div></section>
</main>
<footer style="text-align:center;padding:16px;color:#62717e;font-size:11px">BPFCoBrain remains authoritative · visualization layer only</footer>

<script>
const pos={fred:[50,13],bob:[13,36],cindy:[35,49],kai:[65,49],neo:[87,36]};
async function load(){
 const d=await fetch("/api").then(r=>r.json());
 t.textContent=new Date().toLocaleTimeString();
 a.innerHTML=d.agents.map(x=>`<div class=card><div class=face>${x[1][0]}</div><b>${x[1]}</b><div class=muted>${x[2]}</div></div>`).join("");
 k.innerHTML=`<div class=stat>Notes<b>${d.knowledge.notes.toLocaleString()}</b></div><div class=stat>Words<b>${d.knowledge.words.toLocaleString()}</b></div><div class=stat>Connections<b>${d.knowledge.connections.toLocaleString()}</b></div><div class=stat>Unresolved<b class=warn>${d.knowledge.unresolved.toLocaleString()}</b></div>`;
 source.textContent="Source: "+d.knowledge.source;
 s.innerHTML=Object.entries(d.system).map(([n,v])=>`<div class=row><span>${n}</span><b class=${v==="READY"||v==="ONLINE"||v==="CLEAN"?"ok":v==="OFFLINE"?"warn":""}>${v}</b></div>`).join("");
 draw(d.knowledge,d.agents);
}
function draw(k,agents){
 const g=document.getElementById("graph"),w=g.clientWidth,h=470;
 const P={}; for(const [id,p] of Object.entries(pos))P[id]=[w*p[0]/100,h*p[1]/100];
 let s="<svg viewBox='0 0 "+w+" "+h+"'>";
 for(const id of ["bob","cindy","kai","neo"])s+=`<line class=agentEdge x1=${P.fred[0]} y1=${P.fred[1]+27} x2=${P[id][0]} y2=${P[id][1]-24}/>`;
 for(const e of k.edges){let x=25+(Math.abs(hash(e.source))%50),y=68+(Math.abs(hash(e.target))%23);let x2=72-(Math.abs(hash(e.target))%48),y2=72+(Math.abs(hash(e.source))%23);s+=`<line class=edge x1=${w*x/100} y1=${h*y/100} x2=${w*x2/100} y2=${h*y2/100}/>`}
 for(const [id,p] of Object.entries(pos)){let a=agents.find(x=>x[0]===id);s+=`<circle class=agentNode cx=${p[0]} cy=${p[1]} r=${id==="fred"?29:24}/><text class=nt x=${p[0]} y=${p[1]+4}>${a[1].toUpperCase()}</text>`}
 const ns=k.nodes.slice(0,70);ns.forEach((n,i)=>{let x=8+(i%14)*6.4,y=68+Math.floor(i/14)*6;s+=`<circle class=node cx=${w*x/100} cy=${h*y/100} r=6/><text class=label x=${w*x/100} y=${h*y/100+16}>${esc(n).slice(0,18)}</text>`});s+="</svg>";g.innerHTML=s;
}
function hash(x){let h=0;for(let i=0;i<x.length;i++)h=((h<<5)-h)+x.charCodeAt(i)|0;return h}
function esc(x){return x.replace(/[&<>"']/g,"")}
load();setInterval(load,3000);
</script></body></html>'''

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/api":
            b=json.dumps(payload()).encode()
            self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(b);return
        b=HTML.encode()
        self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.end_headers();self.wfile.write(b)
    def log_message(self,*a): pass

print(f"BPFCo brain-direct dashboard: http://127.0.0.1:{PORT}")
ThreadingHTTPServer(("127.0.0.1",PORT),H).serve_forever()
