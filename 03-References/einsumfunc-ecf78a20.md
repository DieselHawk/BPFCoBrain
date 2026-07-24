---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\einsumfunc.py
imported: 2026-07-24T11:12:40.420143
file_type: .py
---

# einsumfunc.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\einsumfunc.py`

## Content

```py
def __getattr__(attr_name):
    from numpy._core import einsumfunc

    from ._utils import _raise_warning
    ret = getattr(einsumfunc, attr_name, None)
    if ret is None:
        raise AttributeError(
            f"module 'numpy.core.einsumfunc' has no attribute {attr_name}")
    _raise_warning(attr_name, "einsumfunc")
    return ret

```
