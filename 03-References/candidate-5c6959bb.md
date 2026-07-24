---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_internal\models\candidate.py
imported: 2026-07-24T11:13:17.431630
file_type: .py
---

# candidate.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_internal\models\candidate.py`

## Content

```py
from dataclasses import dataclass

from pip._vendor.packaging.version import Version
from pip._vendor.packaging.version import parse as parse_version

from pip._internal.models.link import Link


@dataclass(frozen=True)
class InstallationCandidate:
    """Represents a potential "candidate" for installation."""

    __slots__ = ["name", "version", "link"]

    name: str
    version: Version
    link: Link

    def __init__(self, name: str, version: str, link: Link) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", parse_version(version))
        object.__setattr__(self, "link", link)

    def __str__(self) -> str:
        return f"{self.name!r} candidate (version {self.version} at {self.link})"

```
