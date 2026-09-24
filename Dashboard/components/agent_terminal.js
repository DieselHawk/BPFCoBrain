(() => {
  "use strict";
  if (window.__BPFCO_AGENT_TERMINAL__) return;
  window.__BPFCO_AGENT_TERMINAL__ = true;

  const agents={Fred:{role:"CEO",color:"#78c8ef"},Bob:{role:"Finance",color:"#65d6a6"},Cindy:{role:"Secretary",color:"#ef8fcb"},Kai:{role:"Legal",color:"#c7a3ff"},Neo:{role:"Sales",color:"#ffb45f"}};
  Object.keys(agents).forEach(name=>{agents[name].avatar=`/agent-terminal/avatar/${name.toLowerCase()}.webp`});
  const edges=["n","e","s","w","ne","se","sw","nw"];
  const panel=document.createElement("aside");
  panel.id="bpfcoAgentTerminal";
  panel.setAttribute("aria-label","BPFCo agent terminal");
  panel.innerHTML=`
    <header class="at-header" id="atHandle">
      <div class="at-heading"><i class="at-orb"></i><span class="at-title">AGENT TERMINAL</span></div>
      <div class="at-controls"><button type="button" class="at-mode" id="atMode" aria-label="Switch network mode" title="Switch online or offline">OFFLINE</button><button type="button" id="atCollapse" aria-label="Collapse terminal">−</button></div>
    </header>
    <section class="at-body">
      <nav class="at-agents" id="atAgents" aria-label="Select agent"></nav>
      <div class="at-presence"><div class="at-avatar" id="atAvatar"><img id="atPortrait" alt="Fred portrait" decoding="async"><span id="atInitial">F</span></div><div class="at-identity"><strong id="atName">Fred</strong><small id="atRole">CEO</small></div><div class="at-state" id="atState">READY</div></div>
      <div class="at-log" id="atLog" aria-live="polite"><p class="at-message system">Super Brain local channel ready.</p></div>
      <form class="at-compose" id="atForm"><textarea id="atInput" maxlength="4000" placeholder="Speak to the selected agent…" required></textarea><button id="atSend" type="submit">SEND</button><button id="atQueue" type="button" title="Queue an internal task for this specialist">QUEUE</button></form>
      <details class="at-research"><summary>AGENT RESEARCH REQUESTS</summary><button type="button" id="atResearchRefresh">Refresh requests</button><div id="atResearchList"></div></details>
      <div class="at-status" id="atStatus">External actions remain approval-gated</div>
    </section>
    ${edges.map(edge=>`<i class="at-resize at-resize-${edge}" data-at-resize="${edge}"></i>`).join("")}`;
  document.body.appendChild(panel);

  const $=id=>document.getElementById(id);let selected="Fred",drag=null,resize=null;
  function clamp(){const w=Math.min(panel.offsetWidth,innerWidth),h=Math.min(panel.offsetHeight,innerHeight);panel.style.left=`${Math.max(0,Math.min(innerWidth-w,panel.offsetLeft))}px`;panel.style.top=`${Math.max(0,Math.min(innerHeight-h,panel.offsetTop))}px`;panel.style.right="auto";panel.style.bottom="auto"}
  function save(){if(panel.classList.contains("at-collapsed"))return;localStorage.setItem("bpfco.agentTerminal.overlay",JSON.stringify({left:panel.offsetLeft,top:panel.offsetTop,width:panel.offsetWidth,height:panel.offsetHeight}))}
  function restore(){try{const g=JSON.parse(localStorage.getItem("bpfco.agentTerminal.overlay"));if(!g)return;panel.style.left=`${g.left}px`;panel.style.top=`${g.top}px`;panel.style.right="auto";panel.style.bottom="auto";panel.style.width=`${g.width}px`;panel.style.height=`${g.height}px`;clamp()}catch(_){localStorage.removeItem("bpfco.agentTerminal.overlay")}}
  function state(value){$("atState").textContent=value;$("atAvatar").className=`at-avatar ${value.toLowerCase()}`}
  function choose(name){selected=name;panel.style.setProperty("--at-accent",agents[name].color);document.querySelectorAll(".at-agent").forEach(b=>b.classList.toggle("active",b.dataset.agent===name));$("atName").textContent=name;$("atRole").textContent=agents[name].role;$("atInitial").textContent=name[0];$("atPortrait").src=agents[name].avatar;$("atPortrait").alt=`${name} portrait`;$("atSend").textContent=name==="Fred"?"TASK FRED":"SEND";$("atQueue").hidden=name==="Fred";$("atForm").classList.toggle("at-fred",name==="Fred");$("atInput").placeholder=name==="Fred"?"Give Fred an internal objective…":"Speak to the selected agent…";state("READY")}
  function message(kind,text){const p=document.createElement("p");p.className=`at-message ${kind}`;p.textContent=text;$("atLog").appendChild(p);$("atLog").scrollTop=$("atLog").scrollHeight}
  async function api(url,options={}){const response=await fetch(url,options),data=await response.json();if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);return data}

  let networkMode="offline";
  function showNetworkMode(mode){
    networkMode=mode==="online"?"online":"offline";
    $("atMode").textContent=networkMode.toUpperCase();
    $("atMode").setAttribute("aria-label",`Network mode ${networkMode}; switch mode`);
    $("atMode").title=`Switch to ${networkMode==="online"?"offline":"online"}`;
  }
  api("/api/agent-terminal/status").then(data=>showNetworkMode(data.network_mode))
    .catch(()=>showNetworkMode("offline"));
  $("atMode").addEventListener("pointerdown",event=>event.stopPropagation());
  $("atMode").addEventListener("click",async event=>{
    event.stopPropagation();
    const target=networkMode==="online"?"offline":"online";
    $("atMode").disabled=true;
    try{
      const data=await api("/api/agent-terminal/network-mode",{
        method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({mode:target})
      });
      showNetworkMode(data.network_mode);
      message("system",`Network mode: ${target}. Existing workers need restart to inherit it.`);
    }catch(error){message("system",error.message)}
    finally{$("atMode").disabled=false}
  });

  async function refreshResearchRequests(){
    const list=$("atResearchList");list.textContent="Loading…";
    try{
      const data=await api("/api/agent-terminal/research-requests");
      list.textContent="";
      if(!data.requests.length){list.textContent="No research requests.";return}
      data.requests.forEach(item=>{
        const row=document.createElement("div");
        row.className="at-research-item";
        const label=document.createElement("p");
        label.textContent=`${item.agent} · ${item.status} · ${item.query}`;
        row.appendChild(label);
        if(item.status==="requested"){
          const input=document.createElement("input");
          input.placeholder="Guidance for Fred (optional)";
          input.maxLength=1000;
          input.value=item.guidance||"";
          const button=document.createElement("button");
          button.type="button";button.textContent="Guide";
          button.onclick=async()=>{
            button.disabled=true;
            try{
              await api(`/api/agent-terminal/research-requests/${item.request_id}/guide`,{
                method:"POST",headers:{"Content-Type":"application/json"},
                body:JSON.stringify({guidance:input.value})
              });
              await refreshResearchRequests();
            }catch(error){message("system",error.message);button.disabled=false}
          };
          row.append(input,button);
        }
        if(item.result){
          const source=document.createElement("p");
          source.textContent=`Source: ${item.result.source_url}`;
          row.appendChild(source);
        }
        list.appendChild(row);
      });
    }catch(error){list.textContent=error.message}
  }
  $("atResearchRefresh").addEventListener("click",refreshResearchRequests);
  refreshResearchRequests();

  Object.entries(agents).forEach(([name,meta])=>{const button=document.createElement("button");button.type="button";button.className="at-agent";button.dataset.agent=name;button.textContent=name;button.style.setProperty("--agent",meta.color);button.onclick=()=>choose(name);$("atAgents").appendChild(button)});
  $("atForm").addEventListener("submit",async event=>{
    event.preventDefault();const objective=$("atInput").value.trim();if(!objective)return;
    const agent=selected,isFred=agent==="Fred";
    message("user",objective);$("atInput").value="";$("atSend").disabled=true;
    state("THINKING");$("atStatus").textContent=`${agent} is thinking through local Ollama…`;
    try{
      const route=isFred?"/api/agent-terminal/fred-task":"/api/agent-terminal/interact";
      const body=isFred?{objective}:{agent,message:objective};
      const result=await api(route,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
      message("reply",`${agent}: ${result.response}`);
      if(isFred){
        const paths=(result.sources||[]).map(source=>source.path);
        message("system",`Task ${result.task_id} · Evidence: ${paths.length?paths.join(", "):"no matching local notes"}`);
      }
      state("SPEAKING");$("atStatus").textContent=`${agent} · local response`;
    }catch(error){message("system",error.message);state("READY");$("atStatus").textContent="Local interaction unavailable"}
    finally{$("atSend").disabled=false}
  });
  const taskAgents={Bob:"Bob_Finance",Cindy:"Cindy_Secretary",Kai:"Kai_Legal",Neo:"Neo_Sales"};
  $("atQueue").addEventListener("click",async()=>{
    const objective=$("atInput").value.trim(),agent=taskAgents[selected];
    if(!objective||!agent)return;
    $("atQueue").disabled=true;
    try{
      const result=await api("/api/dispatch",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({agent,objective})});
      message("system",`Queued ${agent}: ${result.task.task_id} · ${objective}`);
      $("atInput").value="";$("atStatus").textContent="Internal task queued for CEO orchestration";
    }catch(error){message("system",error.message)}
    finally{$("atQueue").disabled=false}
  });
  $("atCollapse").addEventListener("click",event=>{event.stopPropagation();panel.classList.toggle("at-collapsed");event.currentTarget.textContent=panel.classList.contains("at-collapsed")?"+":"−";event.currentTarget.setAttribute("aria-label",panel.classList.contains("at-collapsed")?"Restore terminal":"Collapse terminal");clamp()});

  const handle=$("atHandle");handle.addEventListener("pointerdown",event=>{if(event.target.closest("button"))return;const box=panel.getBoundingClientRect();drag={x:event.clientX-box.left,y:event.clientY-box.top};panel.classList.add("at-dragging");handle.setPointerCapture(event.pointerId)});handle.addEventListener("pointermove",event=>{if(!drag)return;panel.style.left=`${event.clientX-drag.x}px`;panel.style.top=`${event.clientY-drag.y}px`;panel.style.right="auto";panel.style.bottom="auto";clamp()});handle.addEventListener("pointerup",()=>{drag=null;panel.classList.remove("at-dragging");save()});
  document.querySelectorAll("[data-at-resize]").forEach(grip=>{grip.addEventListener("pointerdown",event=>{event.preventDefault();event.stopPropagation();const box=panel.getBoundingClientRect();resize={edge:grip.dataset.atResize,startX:event.clientX,startY:event.clientY,left:box.left,top:box.top,width:box.width,height:box.height};grip.setPointerCapture(event.pointerId)});grip.addEventListener("pointermove",event=>{if(!resize)return;const dx=event.clientX-resize.startX,dy=event.clientY-resize.startY;let {left,top,width,height}=resize;if(resize.edge.includes("e"))width+=dx;if(resize.edge.includes("s"))height+=dy;if(resize.edge.includes("w")){width-=dx;left+=dx}if(resize.edge.includes("n")){height-=dy;top+=dy}width=Math.max(330,Math.min(innerWidth-Math.max(0,left),width));height=Math.max(330,Math.min(innerHeight-Math.max(0,top),height));if(resize.edge.includes("w"))left=resize.left+resize.width-width;if(resize.edge.includes("n"))top=resize.top+resize.height-height;panel.style.left=`${Math.max(0,left)}px`;panel.style.top=`${Math.max(0,top)}px`;panel.style.right="auto";panel.style.bottom="auto";panel.style.width=`${width}px`;panel.style.height=`${height}px`});grip.addEventListener("pointerup",()=>{resize=null;save()})});

  addEventListener("resize",clamp);restore();choose("Fred");api("/api/agent-terminal/status").then(s=>{$("atMode").textContent=`${s.network_mode.toUpperCase()} · ${s.renderer.toUpperCase()}`}).catch(()=>{});
})();
