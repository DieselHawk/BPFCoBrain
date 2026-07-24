---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\_backends\__init__.py
imported: 2026-07-24T11:12:44.681981
file_type: .py
---

# __init__.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\f2py\_backends\__init__.py`

## Content

```py
def f2py_build_generator(name):
    if name == "meson":
        from ._meson import MesonBackend
        return MesonBackend
    else:
        raise ValueError(f"Unknown backend: {name}")

```
