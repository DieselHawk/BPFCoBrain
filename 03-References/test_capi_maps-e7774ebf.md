---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\test_capi_maps.py
imported: 2026-07-24T11:12:44.458283
file_type: .py
---

# test_capi_maps.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\test_capi_maps.py`

## Content

```py
from numpy.f2py import capi_maps


def test_complex_long_double_capi_map():
    assert capi_maps.c2capi_map["complex_long_double"] == "NPY_CLONGDOUBLE"


def test_complex_long_double_is_distinct():
    assert capi_maps.c2pycode_map["complex_long_double"] != capi_maps.c2pycode_map["complex_double"]
    assert capi_maps.c2capi_map["complex_long_double"] != capi_maps.c2capi_map["complex_double"]

```
