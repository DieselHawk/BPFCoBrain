---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\flatiter.py
imported: 2026-07-24T11:13:00.516743
file_type: .py
---

# flatiter.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\flatiter.py`

## Content

```py
import numpy as np

a = np.empty((2, 2)).flat

a.base
a.copy()
a.coords
a.index
iter(a)
next(a)
a[0]
a[...]
a[:]
a.__array__()

b = np.array([1]).flat
a[b]

a[0] = "1"
a[:] = "2"
a[...] = "3"
a[[]] = "4"
a[[0]] = "5"
a[[[0]]] = "6"
a[[[[[0]]]]] = "7"
a[b] = "8"

```
