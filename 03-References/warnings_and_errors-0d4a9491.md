---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\warnings_and_errors.py
imported: 2026-07-24T11:13:00.731708
file_type: .py
---

# warnings_and_errors.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\warnings_and_errors.py`

## Content

```py
import numpy.exceptions as ex

ex.AxisError("test")
ex.AxisError(1, ndim=2)
ex.AxisError(1, ndim=2, msg_prefix="error")
ex.AxisError(1, ndim=2, msg_prefix=None)

```
