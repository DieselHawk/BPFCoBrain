---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\tests\test_perfect_graph.py
imported: 2026-07-24T11:12:21.110588
file_type: .py
---

# test_perfect_graph.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\tests\test_perfect_graph.py`

## Content

```py
import networkx as nx


def test_chordal_graph():
    G = nx.complete_graph(5)
    assert nx.is_perfect_graph(G)


def test_odd_cycle():
    G = nx.cycle_graph(5)  # Induced odd cycle
    assert not nx.is_perfect_graph(G)


def test_even_cycle():
    G = nx.cycle_graph(6)  # Even cycle is perfect
    assert nx.is_perfect_graph(G)


def test_complement_of_odd_cycle():
    G = nx.cycle_graph(7)
    GC = nx.complement(G)
    assert not nx.is_perfect_graph(GC)


def test_disconnected_union_of_cliques():
    G = nx.disjoint_union(nx.complete_graph(3), nx.complete_graph(4))
    assert nx.is_perfect_graph(G)

```
