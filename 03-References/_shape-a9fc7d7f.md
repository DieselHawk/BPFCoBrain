---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\_typing\_shape.py
imported: 2026-07-24T11:13:12.504627
file_type: .py
---

# _shape.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\_typing\_shape.py`

## Content

```py
from collections.abc import Sequence
from typing import Any, SupportsIndex

type _Shape = tuple[int, ...]
type _AnyShape = tuple[Any, ...]

# Anything that can be coerced to a shape tuple
type _ShapeLike = SupportsIndex | Sequence[SupportsIndex]

```
