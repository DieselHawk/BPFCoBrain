---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\_utils\_conversions.py
imported: 2026-07-24T11:13:12.528657
file_type: .py
---

# _conversions.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\_utils\_conversions.py`

## Content

```py
"""
A set of methods retained from np.compat module that
are still used across codebase.
"""

__all__ = ["asunicode", "asbytes"]


def asunicode(s):
    if isinstance(s, bytes):
        return s.decode('latin1')
    return str(s)


def asbytes(s):
    if isinstance(s, bytes):
        return s
    return str(s).encode('latin1')

```
