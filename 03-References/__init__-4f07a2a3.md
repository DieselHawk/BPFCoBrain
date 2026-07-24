---
type: imported
source: C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\rapidfuzz\distance\__init__.py
imported: 2026-07-24T11:13:48.924428
file_type: .py
---

# __init__.py

**Original:** `C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Lib\site-packages\rapidfuzz\distance\__init__.py`

## Content

```py
# SPDX-License-Identifier: MIT
# Copyright (C) 2022 Max Bachmann

from __future__ import annotations

from . import (
    OSA,
    DamerauLevenshtein,
    Hamming,
    Indel,
    Jaro,
    JaroWinkler,
    LCSseq,
    Levenshtein,
    Postfix,
    Prefix,
)
from ._initialize import Editop, Editops, MatchingBlock, Opcode, Opcodes, ScoreAlignment

__all__ = [
    "OSA",
    "DamerauLevenshtein",
    "Editop",
    "Editops",
    "Hamming",
    "Indel",
    "Jaro",
    "JaroWinkler",
    "LCSseq",
    "Levenshtein",
    "MatchingBlock",
    "Opcode",
    "Opcodes",
    "Postfix",
    "Prefix",
    "ScoreAlignment",
]

```
