---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\generators\tests\test_triads.py
imported: 2026-07-24T11:12:32.670428
file_type: .py
---

# test_triads.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\networkx\generators\tests\test_triads.py`

## Content

```py
"""Unit tests for the :mod:`networkx.generators.triads` module."""

import pytest

from networkx import triad_graph


def test_triad_graph():
    G = triad_graph("030T")
    assert [tuple(e) for e in ("ab", "ac", "cb")] == sorted(G.edges())


def test_invalid_name():
    with pytest.raises(ValueError):
        triad_graph("bogus")

```
