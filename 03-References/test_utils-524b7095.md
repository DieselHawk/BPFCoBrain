---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\community\tests\test_utils.py
imported: 2026-07-24T11:12:09.910147
file_type: .py
---

# test_utils.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\community\tests\test_utils.py`

## Content

```py
"""Unit tests for the :mod:`networkx.algorithms.community.utils` module."""

import networkx as nx


def test_is_partition():
    G = nx.empty_graph(3)
    assert nx.community.is_partition(G, [{0, 1}, {2}])
    assert nx.community.is_partition(G, ({0, 1}, {2}))
    assert nx.community.is_partition(G, ([0, 1], [2]))
    assert nx.community.is_partition(G, [[0, 1], [2]])


def test_not_covering():
    G = nx.empty_graph(3)
    assert not nx.community.is_partition(G, [{0}, {1}])


def test_not_disjoint():
    G = nx.empty_graph(3)
    assert not nx.community.is_partition(G, [{0, 1}, {1, 2}])


def test_not_node():
    G = nx.empty_graph(3)
    assert not nx.community.is_partition(G, [{0, 1}, {3}])

```
