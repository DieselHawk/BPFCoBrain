---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\defchararray.py
imported: 2026-07-24T11:12:40.412997
file_type: .py
---

# defchararray.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\defchararray.py`

## Content

```py
def __getattr__(attr_name):
    from numpy._core import defchararray

    from ._utils import _raise_warning
    ret = getattr(defchararray, attr_name, None)
    if ret is None:
        raise AttributeError(
            f"module 'numpy.core.defchararray' has no attribute {attr_name}")
    _raise_warning(attr_name, "defchararray")
    return ret

```
