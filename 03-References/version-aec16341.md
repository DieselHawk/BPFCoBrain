---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\version.py
imported: 2026-07-24T11:12:40.343640
file_type: .py
---

# version.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\version.py`

## Content

```py

"""
Module to expose more detailed version info for the installed `numpy`
"""
version = "2.5.1"
__version__ = version
full_version = version

git_revision = "5e1d03ffac5f2c0a9c39bfcaa9fc853b2b83151e"
release = 'dev' not in version and '+' not in version
short_version = version.split("+")[0]

```
