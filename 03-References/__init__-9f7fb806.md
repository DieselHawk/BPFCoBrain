---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_vendor\cachecontrol\__init__.py
imported: 2026-07-24T11:13:25.941397
file_type: .py
---

# __init__.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\pip\_vendor\cachecontrol\__init__.py`

## Content

```py
# SPDX-FileCopyrightText: 2015 Eric Larson
#
# SPDX-License-Identifier: Apache-2.0

"""CacheControl import Interface.

Make it easy to import from cachecontrol without long namespaces.
"""

__author__ = "Eric Larson"
__email__ = "eric@ionrock.org"
__version__ = "0.14.1"

from pip._vendor.cachecontrol.adapter import CacheControlAdapter
from pip._vendor.cachecontrol.controller import CacheController
from pip._vendor.cachecontrol.wrapper import CacheControl

__all__ = [
    "__author__",
    "__email__",
    "__version__",
    "CacheControlAdapter",
    "CacheController",
    "CacheControl",
]

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

```
