---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_vendor\resolvelib\compat\collections_abc.py
imported: 2026-07-24T11:13:37.349588
file_type: .py
---

# collections_abc.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_vendor\resolvelib\compat\collections_abc.py`

## Content

```py
__all__ = ["Mapping", "Sequence"]

try:
    from collections.abc import Mapping, Sequence
except ImportError:
    from collections import Mapping, Sequence

```
