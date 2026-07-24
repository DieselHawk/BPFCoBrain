---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\_dtype.py
imported: 2026-07-24T11:12:40.490449
file_type: .py
---

# _dtype.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\_dtype.py`

## Content

```py
def __getattr__(attr_name):
    from numpy._core import _dtype

    from ._utils import _raise_warning
    ret = getattr(_dtype, attr_name, None)
    if ret is None:
        raise AttributeError(
            f"module 'numpy.core._dtype' has no attribute {attr_name}")
    _raise_warning(attr_name, "_dtype")
    return ret

```
