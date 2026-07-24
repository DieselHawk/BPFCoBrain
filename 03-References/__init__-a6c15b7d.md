---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\__init__.py
imported: 2026-07-24T11:12:44.661227
file_type: .py
---

# __init__.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\__init__.py`

## Content

```py
import pytest

from numpy.testing import IS_EDITABLE, IS_WASM

if IS_WASM:
    pytest.skip(
        "WASM/Pyodide does not use or support Fortran",
        allow_module_level=True
    )


if IS_EDITABLE:
    pytest.skip(
        "Editable install doesn't support tests with a compile step",
        allow_module_level=True
    )

```
