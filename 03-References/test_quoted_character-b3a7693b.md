---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\test_quoted_character.py
imported: 2026-07-24T11:12:44.562028
file_type: .py
---

# test_quoted_character.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\tests\test_quoted_character.py`

## Content

```py
"""See https://github.com/numpy/numpy/pull/10676.

"""
import sys

import pytest

from . import util


# Note: do not mark as slow! This is one of a small set of f2py compile tests retained
# in the default suite invocation for compile-path coverage.
class TestQuotedCharacter(util.F2PyTest):
    sources = [util.getpath("tests", "src", "quoted_character", "foo.f")]

    @pytest.mark.skipif(sys.platform == "win32",
                        reason="Fails with MinGW64 Gfortran (Issue #9673)")
    def test_quoted_character(self):
        assert self.module.foo() == (b"'", b'"', b";", b"!", b"(", b")")

```
