"""Create and restore-check a bounded offline archive of Fred's live state.

This script never writes into the live checkout. Archive data is unencrypted;
choose a trusted existing offline destination.
"""
import argparse
import hashlib
import json
import os
import secrets
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile

MAX_FILE_BYTES = 100 * 1024 * 1024
MAX_TOTAL_BYTES = 1024 * 1024 * 1024
MAX_FILES = 10000
CHUNK = 1024 * 1024
SKIP_DIRS = {"__pycache__", ".git", ".venv", "node_modules"}
MANIFEST = "backup-manifest.json"


def _offline_destination(destination, live):
    path = Path(destination).expanduser().resolve(strict=True)
    if not path.is_dir() or path == live or live in path.parents:
        raise ValueError("Choose an existing folder outside the live checkout")
    if "onedrive" in (part.casefold() for part in path.parts):
        raise ValueError("Choose an offline folder outside OneDrive")
    if os.name == "nt":
        import ctypes
        anchor = Path(path.anchor)
        if ctypes.windll.kernel32.GetDriveTypeW(str(anchor)) == 4:
            raise ValueError("Network drives are not offline backup destinations")
    return path


def _candidates(live):
    executive = live / "Brain" / "Executive"
    index = live / ".vault-index.json"
    if not executive.is_dir() or not index.is_file():
        raise ValueError("Live Executive directory or vault index is missing")
    paths = [index]
    for path in executive.rglob("*"):
        relative = path.relative_to(live)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError("Symlink inside Executive directory: " + str(relative))
        if path.is_file() and path.suffix.lower() not in {".pyc", ".tmp"}:
            paths.append(path)
    paths = sorted(paths, key=lambda item: item.relative_to(live).as_posix())
    if len(paths) > MAX_FILES:
        raise ValueError("Backup exceeds file-count limit")
    signatures = {}
    total = 0
    for path in paths:
        stat = path.stat()
        if stat.st_size > MAX_FILE_BYTES:
            raise ValueError("Backup file exceeds size limit: " + str(path.relative_to(live)))
        total += stat.st_size
        signatures[path.relative_to(live).as_posix()] = (stat.st_size, stat.st_mtime_ns)
    if total > MAX_TOTAL_BYTES:
        raise ValueError("Backup exceeds total-size limit")
    return paths, signatures, total


def _hash_copy(source, target):
    digest = hashlib.sha256()
    size = 0
    with source as stream:
        while True:
            chunk = stream.read(CHUNK)
            if not chunk:
                break
            target.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def restore_check(archive_path, destination):
    """Extract into a disposable folder and check every file before deletion."""
    destination = Path(destination)
    with ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read(MANIFEST))
        expected = manifest["files"]
        if set(archive.namelist()) != set(expected) | {MANIFEST}:
            raise ValueError("Archive member list differs from manifest")
        with tempfile.TemporaryDirectory(prefix="fred-restore-check-", dir=destination) as temp:
            restored = Path(temp)
            for name, meta in expected.items():
                posix = PurePosixPath(name)
                if posix.is_absolute() or ".." in posix.parts or not name:
                    raise ValueError("Unsafe archive member")
                target = restored.joinpath(*posix.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(name) as source, target.open("xb") as sink:
                    size, digest = _hash_copy(source, sink)
                if size != meta["bytes"] or digest != meta["sha256"]:
                    raise ValueError("Restore verification failed: " + name)
            index = restored / ".vault-index.json"
            index_data = json.loads(index.read_text(encoding="utf-8-sig"))
            if not isinstance(index_data.get("notes"), dict):
                raise ValueError("Restored vault index has no notes mapping")
    return len(expected)


def create(live_root, destination):
    live = Path(live_root).expanduser().resolve(strict=True)
    destination = _offline_destination(destination, live)
    paths, signatures, total = _candidates(live)
    if shutil.disk_usage(destination).free < 2 * total + 64 * 1024 * 1024:
        raise ValueError("Insufficient free space for archive and restore check")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    archive = destination / ("fred-runtime-" + stamp + "-" + secrets.token_hex(3) + ".zip")
    partial = archive.with_suffix(".partial")
    manifest = {"format": 1, "created_at": datetime.now(timezone.utc).isoformat(),
                "scope": ["Brain/Executive", ".vault-index.json"], "files": {}}
    try:
        with ZipFile(partial, "x", compression=ZIP_DEFLATED, compresslevel=3) as out:
            for path in paths:
                name = path.relative_to(live).as_posix()
                before = signatures[name]
                with path.open("rb") as source, out.open(name, "w") as sink:
                    size, digest = _hash_copy(source, sink)
                after = path.stat()
                if before != (after.st_size, after.st_mtime_ns) or size != before[0]:
                    raise RuntimeError("Source changed during backup: " + name)
                manifest["files"][name] = {"bytes": size, "sha256": digest}
            out.writestr(MANIFEST, json.dumps(manifest, indent=2))
        _, final_signatures, _ = _candidates(live)
        if final_signatures != signatures:
            raise RuntimeError("Live records changed during backup; retry when idle")
        count = restore_check(partial, destination)
        partial.replace(archive)
        return archive, count, total
    finally:
        partial.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    try:
        archive, count, size = create(args.live, args.destination)
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        parser.exit(1, "Backup stopped: " + str(exc) + "\n")
    print("Archive: " + str(archive))
    print("Restore check passed: " + str(count) + " files, " + str(size) + " source bytes")
    print("Scope: Brain/Executive and .vault-index.json; document files are not in this archive")


if __name__ == "__main__":
    main()
