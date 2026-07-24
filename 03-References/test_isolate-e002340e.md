---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\tests\test_isolate.py
imported: 2026-07-24T11:12:21.063270
file_type: .py
---

# test_isolate.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\tests\test_isolate.py`

## Content

```py
"""Unit tests for the :mod:`networkx.algorithms.isolates` module."""

import networkx as nx


def test_is_isolate():
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_node(2)
    assert not nx.is_isolate(G, 0)
    assert not nx.is_isolate(G, 1)
    assert nx.is_isolate(G, 2)


def test_isolates():
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_nodes_from([2, 3])
    assert sorted(nx.isolates(G)) == [2, 3]


def test_number_of_isolates():
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_nodes_from([2, 3])
    assert nx.number_of_isolates(G) == 2

```
