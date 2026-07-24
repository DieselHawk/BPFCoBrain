---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\numerictypes.py
imported: 2026-07-24T11:12:40.457651
file_type: .py
---

# numerictypes.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\core\numerictypes.py`

## Content

```py
def __getattr__(attr_name):
    from numpy._core import numerictypes

    from ._utils import _raise_warning
    ret = getattr(numerictypes, attr_name, None)
    if ret is None:
        raise AttributeError(
            f"module 'numpy.core.numerictypes' has no attribute {attr_name}")
    _raise_warning(attr_name, "numerictypes")
    return ret

```
