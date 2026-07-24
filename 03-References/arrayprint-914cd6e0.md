---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\arrayprint.py
imported: 2026-07-24T11:12:40.407733
file_type: .py
---

# arrayprint.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\arrayprint.py`

## Content

```py
def __getattr__(attr_name):
    from numpy._core import arrayprint

    from ._utils import _raise_warning
    ret = getattr(arrayprint, attr_name, None)
    if ret is None:
        raise AttributeError(
            f"module 'numpy.core.arrayprint' has no attribute {attr_name}")
    _raise_warning(attr_name, "arrayprint")
    return ret

```
