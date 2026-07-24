---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\lib_version.py
imported: 2026-07-24T11:13:00.567729
file_type: .py
---

# lib_version.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\typing\tests\data\pass\lib_version.py`

## Content

```py
from numpy.lib import NumpyVersion

version = NumpyVersion("1.8.0")

version.vstring
version.version
version.major
version.minor
version.bugfix
version.pre_release
version.is_devversion

version == version
version != version
version < "1.8.0"
version <= version
version > version
version >= "1.8.0"

```
