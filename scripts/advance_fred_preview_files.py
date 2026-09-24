"""Advance only verified older preview files to fetched draft blobs, with rollback."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Verified local Git blob IDs supplied from the isolated Fred preview.
ALLOWED_OLD = {
    'Dashboard/super_brain_3d.html': '743e9f79bcd8358bd4ddaa2f83d34cfeeb85a56b',
    'Dashboard/adapters/provenance_edges.py': '06bea1db1a567cb51a00fc71a19392c34ee365c0',
    'ceo_dashboard.py': 'a88fe6f0fc1d57021bd7ac57da71e30400604fc0',
}
PATHS = (
    'Dashboard/super_brain_3d.html',
    'Dashboard/adapters/provenance_edges.py',
    'Dashboard/adapters/note_edges.py',
    'Dashboard/adapters/document_edges.py',
    'ceo_dashboard.py',
    'run_fred_preview.py',
)


def blob_id(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def advance(repo, ref, check_only=False):
    if not (repo / '.git').exists():
        raise ValueError('Expected an isolated Git worktree')
    origin = git(repo, 'remote', 'get-url', 'origin').decode().strip()
    if not origin.rstrip('/').endswith(('DieselHawk/BPFCoBrain', 'DieselHawk/BPFCoBrain.git')):
        raise ValueError('Unexpected repository origin')
    operations = []
    for relative in PATHS:
        destination = repo / relative
        fetched = git(repo, 'show', f'{ref}:{relative}')
        wanted = blob_id(fetched)
        current = destination.read_bytes() if destination.exists() else None
        previous = git(repo, 'hash-object', '--', relative).decode().strip() if current is not None else None
        if current is not None and previous not in (wanted, ALLOWED_OLD.get(relative)):
            raise ValueError(f'Unrecognized local change; left intact: {relative}; local={previous}; draft={wanted}; accepted_old={ALLOWED_OLD.get(relative)}')
        if current is None and relative in ALLOWED_OLD:
            raise ValueError(f'Expected known preview file is missing: {relative}')
        operations.append((relative, destination, current, fetched, previous, wanted))
    if check_only:
        print('All six preview files are recognized; no files changed.')
        return None
    backup = Path(tempfile.mkdtemp(prefix='fred-preview-reconcile-'))
    for relative, _, current, _, _, _ in operations:
        if current is not None:
            target = backup / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(current)
    (backup / 'manifest.json').write_text(json.dumps([
        {'path': relative, 'before': before, 'draft': after}
        for relative, _, _, _, before, after in operations
    ], indent=2), encoding='utf-8')
    changed = []
    try:
        for relative, destination, current, fetched, previous, wanted in operations:
            if previous == wanted:
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stage:
                stage.write(fetched)
                staged = Path(stage.name)
            os.replace(staged, destination)
            changed.append((destination, current))
        check = [str(repo / relative) for relative in PATHS if relative.endswith('.py')]
        subprocess.run([sys.executable, '-m', 'py_compile', *check],
                       cwd=repo, check=True)
        for _, destination, _, _, _, wanted in operations:
            if blob_id(destination.read_bytes()) != wanted:
                raise RuntimeError(f'File changed during verification: {destination}')
    except Exception:
        for destination, current in reversed(changed):
            if current is None:
                destination.unlink(missing_ok=True)
            else:
                destination.write_bytes(current)
        raise
    print(f'Advanced {len(changed)} verified files; earlier bytes backed up at {backup}')
    return backup


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('preview', type=Path)
    parser.add_argument('--ref', default='FETCH_HEAD')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    advance(args.preview.resolve(), args.ref, args.check_only)
