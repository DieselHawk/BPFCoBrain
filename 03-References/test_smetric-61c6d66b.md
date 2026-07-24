---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\tests\test_smetric.py
imported: 2026-07-24T11:12:21.180198
file_type: .py
---

# test_smetric.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\algorithms\tests\test_smetric.py`

## Content

```py
import pytest

import networkx as nx


def test_smetric():
    G = nx.Graph([(1, 2), (2, 3), (2, 4), (1, 4)])
    assert nx.s_metric(G) == 19.0

```
