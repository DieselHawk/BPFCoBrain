---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\linalg\tests\test_deprecations.py
imported: 2026-07-24T11:12:52.767856
file_type: .py
---

# test_deprecations.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\numpy\linalg\tests\test_deprecations.py`

## Content

```py
"""Test deprecation and future warnings.

"""
import pytest

import numpy as np


def test_qr_mode_full_future_warning():
    """Check mode='full' FutureWarning.

    In numpy 1.8 the mode options 'full' and 'economic' in linalg.qr were
    deprecated. The release date will probably be sometime in the summer
    of 2013.

    """
    a = np.eye(2)
    pytest.warns(DeprecationWarning, np.linalg.qr, a, mode='full')
    pytest.warns(DeprecationWarning, np.linalg.qr, a, mode='f')
    pytest.warns(DeprecationWarning, np.linalg.qr, a, mode='economic')
    pytest.warns(DeprecationWarning, np.linalg.qr, a, mode='e')

```
