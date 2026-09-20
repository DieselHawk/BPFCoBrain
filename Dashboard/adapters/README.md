# BPFCo Super Brain Renderer Contract

The existing BPFCo D3 graph is the current working renderer.

The future 3D renderer is the official:
https://github.com/vasturiano/3d-force-graph

Target:
3d-force-graph 1.80.0

The renderer receives normalized BPFCo graph data:

nodes:
- id
- label
- path
- folder
- word_count
- connection_count
- agent_hint

links:
- source
- target

The renderer MUST NOT become the source of truth.
BPFCoBrain remains authoritative.

The renderer must support:
- starfield background
- 3D orbit/camera
- zoom and focus
- visible relationships
- directional/animated connections
- node selection
- context inspection
- agent presence overlay

Fallback:
If the 3D renderer is unavailable, the existing D3 graph remains active.

Wi-Fi-only dependencies:
- 3d-force-graph
- Three.js
- three-forcegraph
- related npm dependency tree

No dependency installation is required for this contract commit.
