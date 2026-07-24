---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\minors\__init__.py
imported: 2026-07-24T11:12:17.348163
file_type: .py
---

# __init__.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\minors\__init__.py`

## Content

```py
"""
Subpackages related to graph-minor problems.

In graph theory, an undirected graph H is called a minor of the graph G if H
can be formed from G by deleting edges and vertices and by contracting edges
[1]_.

References
----------
.. [1] https://en.wikipedia.org/wiki/Graph_minor
"""

from networkx.algorithms.minors.contraction import (
    contracted_edge,
    contracted_nodes,
    equivalence_classes,
    identified_nodes,
    quotient_graph,
)

__all__ = [
    "contracted_edge",
    "contracted_nodes",
    "equivalence_classes",
    "identified_nodes",
    "quotient_graph",
]

```
