---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_internal\distributions\__init__.py
imported: 2026-07-24T11:13:16.999194
file_type: .py
---

# __init__.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_internal\distributions\__init__.py`

## Content

```py
from pip._internal.distributions.base import AbstractDistribution
from pip._internal.distributions.sdist import SourceDistribution
from pip._internal.distributions.wheel import WheelDistribution
from pip._internal.req.req_install import InstallRequirement


def make_distribution_for_install_requirement(
    install_req: InstallRequirement,
) -> AbstractDistribution:
    """Returns a Distribution for the given InstallRequirement"""
    # Editable requirements will always be source distributions. They use the
    # legacy logic until we create a modern standard for them.
    if install_req.editable:
        return SourceDistribution(install_req)

    # If it's a wheel, it's a WheelDistribution
    if install_req.is_wheel:
        return WheelDistribution(install_req)

    # Otherwise, a SourceDistribution
    return SourceDistribution(install_req)

```
