---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\fromnumeric.py
imported: 2026-07-24T11:12:40.426026
file_type: .py
---

# fromnumeric.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\fromnumeric.py`

## Content

```py
def __getattr__(attr_name):
    from numpy._core import fromnumeric

    from ._utils import _raise_warning
    ret = getattr(fromnumeric, attr_name, None)
    if ret is None:
        raise AttributeError(
            f"module 'numpy.core.fromnumeric' has no attribute {attr_name}")
    _raise_warning(attr_name, "fromnumeric")
    return ret

```
