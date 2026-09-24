"""Local document source selection shared by retrieval and graph rendering.

Future feeds can use separate adapters; this registry never contacts a service.
"""

import os
from pathlib import Path


def documents_root():
    configured = os.environ.get("BPFCO_DOCUMENTS_ROOT")
    if configured:
        folder = Path(configured).expanduser()
        return folder.resolve() if folder.is_dir() else None
    profile = Path(os.environ.get("USERPROFILE", ""))
    candidates = [Path(r"C:\Documents\New All Docs")]
    if os.environ.get("OneDrive"):
        candidates.append(Path(os.environ["OneDrive"]) / "Documents" / "New All Docs")
    if os.environ.get("USERPROFILE"):
        candidates.append(profile / "OneDrive" / "Documents" / "New All Docs")
    for folder in candidates:
        if folder.is_dir():
            return folder.resolve()
    return None
