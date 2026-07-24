---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\shape_base.py
imported: 2026-07-24T11:12:40.477802
file_type: .py
---

# shape_base.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\shape_base.py`

## Content

```py
def __getattr__(attr_name):
    from numpy._core import shape_base

    from ._utils import _raise_warning
    ret = getattr(shape_base, attr_name, None)
    if ret is None:
        raise AttributeError(
            f"module 'numpy.core.shape_base' has no attribute {attr_name}")
    _raise_warning(attr_name, "shape_base")
    return ret

```
