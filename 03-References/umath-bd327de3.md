---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\umath.py
imported: 2026-07-24T11:12:40.483750
file_type: .py
---

# umath.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\umath.py`

## Content

```py
def __getattr__(attr_name):
    from numpy._core import umath

    from ._utils import _raise_warning
    ret = getattr(umath, attr_name, None)
    if ret is None:
        raise AttributeError(
            f"module 'numpy.core.umath' has no attribute {attr_name}")
    _raise_warning(attr_name, "umath")
    return ret

```
