---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\tests\test_hybrid.py
imported: 2026-07-24T11:12:21.058062
file_type: .py
---

# test_hybrid.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\tests\test_hybrid.py`

## Content

```py
import networkx as nx


def test_2d_grid_graph():
    # FC article claims 2d grid graph of size n is (3,3)-connected
    # and (5,9)-connected, but I don't think it is (5,9)-connected
    G = nx.grid_2d_graph(8, 8, periodic=True)
    assert nx.is_kl_connected(G, 3, 3)
    assert not nx.is_kl_connected(G, 5, 9)
    (H, graphOK) = nx.kl_connected_subgraph(G, 5, 9, same_as_graph=True)
    assert not graphOK


def test_small_graph():
    G = nx.Graph()
    G.add_edge(1, 2)
    G.add_edge(1, 3)
    G.add_edge(2, 3)
    assert nx.is_kl_connected(G, 2, 2)
    H = nx.kl_connected_subgraph(G, 2, 2)
    (H, graphOK) = nx.kl_connected_subgraph(
        G, 2, 2, low_memory=True, same_as_graph=True
    )
    assert graphOK

```
