---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\overrides.py
imported: 2026-07-24T11:12:40.463118
file_type: .py
---

# overrides.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\overrides.py`

## Content

```py
def __getattr__(attr_name):
    from numpy._core import overrides

    from ._utils import _raise_warning
    ret = getattr(overrides, attr_name, None)
    if ret is None:
        raise AttributeError(
            f"module 'numpy.core.overrides' has no attribute {attr_name}")
    _raise_warning(attr_name, "overrides")
    return ret

```
