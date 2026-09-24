"""Bounded backup of Fred's shared runtime state; run when the dashboard is idle."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
SOURCES = (ROOT / "Brain" / "Executive", ROOT / "Shared_Context", ROOT / ".vault-index.json")
EXCLUDE = {"__pycache__", ".git", ".venv", "node_modules", "backups"}
MAX_FILE_BYTES = 100 * 1024 * 1024

def backup(destination):
    destination = Path(destination).expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("Backup destination must be outside the repository.")
    destination.mkdir(parents=True, exist_ok=True)
    candidates = []
    for source in SOURCES:
        if source.is_file():
            candidates.append(source)
        elif source.is_dir():
            candidates.extend(path for path in source.rglob("*") if path.is_file())
    files = []
    for path in sorted(set(candidates)):
        if any(part in EXCLUDE for part in path.relative_to(ROOT).parts):
            continue
        if path.is_symlink():
            continue
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ValueError(f"File exceeds backup limit: {path}")
        files.append(path)
    target = destination / ("fred-state-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".zip")
    if target.exists():
        raise FileExistsError(target)
    manifest = {}
    with ZipFile(target, "x", compression=ZIP_DEFLATED, compresslevel=3) as archive:
        for path in files:
            name = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            manifest[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            archive.writestr(name, data)
        archive.writestr("backup-manifest.json", json.dumps(manifest, indent=2))
    with ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Backup archive failed verification.")
    return target, len(files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", help="Existing separate drive or folder outside the checkout")
    args = parser.parse_args()
    path, count = backup(args.destination)
    print(f"Verified {count} files in {path}")
