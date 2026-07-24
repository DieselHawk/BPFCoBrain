---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\test_isfile.py
imported: 2026-07-24T11:13:00.423442
file_type: .py
---

# test_isfile.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\test_isfile.py`

## Content

```py
import os
from pathlib import Path

import pytest

import numpy as np
from numpy.testing import assert_

ROOT = Path(np.__file__).parents[0]
FILES = [
    ROOT / "py.typed",
    ROOT / "__init__.pyi",
    ROOT / "ctypeslib" / "__init__.pyi",
    ROOT / "_core" / "__init__.pyi",
    ROOT / "f2py" / "__init__.pyi",
    ROOT / "fft" / "__init__.pyi",
    ROOT / "lib" / "__init__.pyi",
    ROOT / "linalg" / "__init__.pyi",
    ROOT / "ma" / "__init__.pyi",
    ROOT / "matrixlib" / "__init__.pyi",
    ROOT / "polynomial" / "__init__.pyi",
    ROOT / "random" / "__init__.pyi",
    ROOT / "testing" / "__init__.pyi",
]


@pytest.mark.thread_unsafe(
    reason="os.path has a thread-safety bug (python/cpython#140054). "
           "Expected to only be a problem in 3.14.0"
)
class TestIsFile:
    def test_isfile(self):
        """Test if all ``.pyi`` files are properly installed."""
        for file in FILES:
            assert_(os.path.isfile(file))

```
