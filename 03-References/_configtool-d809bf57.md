---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\_configtool.py
imported: 2026-07-24T11:12:40.356650
file_type: .py
---

# _configtool.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\_configtool.py`

## Content

```py
import argparse
import sys
from pathlib import Path

from .lib._utils_impl import get_include
from .version import __version__


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print the version and exit.",
    )
    parser.add_argument(
        "--cflags",
        action="store_true",
        help="Compile flag needed when using the NumPy headers.",
    )
    parser.add_argument(
        "--pkgconfigdir",
        action="store_true",
        help=("Print the pkgconfig directory in which `numpy.pc` is stored "
              "(useful for setting $PKG_CONFIG_PATH)."),
    )
    args = parser.parse_args()
    if not sys.argv[1:]:
        parser.print_help()
    if args.cflags:
        print("-I" + get_include())
    if args.pkgconfigdir:
        _path = Path(get_include()) / '..' / 'lib' / 'pkgconfig'
        print(_path.resolve())


if __name__ == "__main__":
    main()

```
