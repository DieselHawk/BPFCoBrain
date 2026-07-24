---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\test_value_attrspec.py
imported: 2026-07-24T11:12:44.647021
file_type: .py
---

# test_value_attrspec.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\test_value_attrspec.py`

## Content

```py
import pytest

from . import util


@pytest.mark.slow
class TestValueAttr(util.F2PyTest):
    sources = [util.getpath("tests", "src", "value_attrspec", "gh21665.f90")]

    # gh-21665
    def test_gh21665(self):
        inp = 2
        out = self.module.fortfuncs.square(inp)
        exp_out = 4
        assert out == exp_out

```
