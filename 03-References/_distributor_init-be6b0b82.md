---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\_distributor_init.py
imported: 2026-07-24T11:12:40.361567
file_type: .py
---

# _distributor_init.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\_distributor_init.py`

## Content

```py
""" Distributor init file

Distributors: you can add custom code here to support particular distributions
of numpy.

For example, this is a good place to put any BLAS/LAPACK initialization code.

The numpy standard source distribution will not put code in this file, so you
can safely replace this file with your own version.
"""

try:
    from . import _distributor_init_local  # noqa: F401
except ImportError:
    pass

```
