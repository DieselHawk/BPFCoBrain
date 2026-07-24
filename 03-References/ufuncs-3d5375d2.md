---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\ufuncs.py
imported: 2026-07-24T11:13:00.716232
file_type: .py
---

# ufuncs.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\ufuncs.py`

## Content

```py
import numpy as np

np.sin(1)
np.sin([1, 2, 3])
np.sin(1, out=np.empty(1))
np.matmul(np.ones((2, 2, 2)), np.ones((2, 2, 2)), axes=[(0, 1), (0, 1), (0, 1)])
np.sin(1, signature="D->D")
# NOTE: `np.generic` subclasses are not guaranteed to support addition;
# re-enable this we can infer the exact return type of `np.sin(...)`.
#
# np.sin(1) + np.sin(1)
np.sin.types[0]
np.sin.__name__
np.sin.__doc__

np.abs(np.array([1]))

```
