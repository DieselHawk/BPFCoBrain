---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_internal\resolution\base.py
imported: 2026-07-24T11:13:21.617440
file_type: .py
---

# base.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_internal\resolution\base.py`

## Content

```py
from typing import Callable, List, Optional

from pip._internal.req.req_install import InstallRequirement
from pip._internal.req.req_set import RequirementSet

InstallRequirementProvider = Callable[
    [str, Optional[InstallRequirement]], InstallRequirement
]


class BaseResolver:
    def resolve(
        self, root_reqs: List[InstallRequirement], check_supported_wheels: bool
    ) -> RequirementSet:
        raise NotImplementedError()

    def get_installation_order(
        self, req_set: RequirementSet
    ) -> List[InstallRequirement]:
        raise NotImplementedError()

```
