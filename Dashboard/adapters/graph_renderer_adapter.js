const BPFCO_RENDERER_CONTRACT = {
  current: "bpfco-d3-2d",
  future: "vasturiano-3d-force-graph",
  version: "1.80.0"
};

function bpfcoNormalizeGraph(raw) {
  const nodes = (raw.nodes || []).map((n, i) => ({
    id: String(n.id ?? n.path ?? n.title ?? i),
    label: String(n.label ?? n.title ?? n.name ?? n.id ?? n.path ?? ""),
    path: n.path ?? "",
    folder: n.folder ?? "",
    word_count: Number(n.word_count ?? 0),
    connection_count: Number(n.connection_count ?? 0),
    agent_hint: n.agent_hint ?? null
  }));

  const links = (raw.links || raw.edges || []).map(e => ({
    source: String(e.source ?? e.from),
    target: String(e.target ?? e.to)
  }));

  return {nodes, links};
}

window.BPFCO_RENDERER_CONTRACT = BPFCO_RENDERER_CONTRACT;
window.bpfcoNormalizeGraph = bpfcoNormalizeGraph;
