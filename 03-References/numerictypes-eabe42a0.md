---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\numerictypes.py
imported: 2026-07-24T11:13:00.653454
file_type: .py
---

# numerictypes.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\numerictypes.py`

## Content

```py
import numpy as np

np.isdtype(np.float64, (np.int64, np.float64))
np.isdtype(np.int64, "signed integer")

np.issubdtype("S1", np.bytes_)
np.issubdtype(np.float64, np.float32)

np.ScalarType
np.ScalarType[0]
np.ScalarType[3]
np.ScalarType[8]
np.ScalarType[10]

np.typecodes["Character"]
np.typecodes["Complex"]
np.typecodes["All"]

```
