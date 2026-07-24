---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_internal\utils\datetime.py
imported: 2026-07-24T11:13:21.756216
file_type: .py
---

# datetime.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_internal\utils\datetime.py`

## Content

```py
"""For when pip wants to check the date or time.
"""

import datetime


def today_is_later_than(year: int, month: int, day: int) -> bool:
    today = datetime.date.today()
    given = datetime.date(year, month, day)

    return today > given

```
