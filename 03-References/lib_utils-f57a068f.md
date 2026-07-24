---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\lib_utils.py
imported: 2026-07-24T11:13:00.556880
file_type: .py
---

# lib_utils.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\lib_utils.py`

## Content

```py
from __future__ import annotations

from io import StringIO

import numpy as np
import numpy.lib.array_utils as array_utils

FILE = StringIO()
AR = np.arange(10, dtype=np.float64)


def func(a: int) -> bool:
    return True


array_utils.byte_bounds(AR)
array_utils.byte_bounds(np.float64())

np.info(1, output=FILE)

```
