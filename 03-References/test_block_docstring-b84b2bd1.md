---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\test_block_docstring.py
imported: 2026-07-24T11:12:44.445037
file_type: .py
---

# test_block_docstring.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\test_block_docstring.py`

## Content

```py
import sys

import pytest

from . import util


@pytest.mark.slow
class TestBlockDocString(util.F2PyTest):
    sources = [util.getpath("tests", "src", "block_docstring", "foo.f")]

    @pytest.mark.skipif(sys.platform == "win32",
                        reason="Fails with MinGW64 Gfortran (Issue #9673)")
    def test_block_docstring(self):
        expected = "bar : 'i'-array(2,3)\n"
        assert self.module.block.__doc__ == expected

```
