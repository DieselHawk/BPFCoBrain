---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\approximation\tests\test_matching.py
imported: 2026-07-24T11:12:01.860255
file_type: .py
---

# test_matching.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\approximation\tests\test_matching.py`

## Content

```py
import networkx as nx
import networkx.algorithms.approximation as a


def test_min_maximal_matching():
    # smoke test
    G = nx.Graph()
    assert len(a.min_maximal_matching(G)) == 0

```
