"""Replace only the verified 3D preview HTML; the running server reads it on reload."""
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RELATIVE = 'Dashboard/super_brain_3d.html'
KNOWN_OLD = {
    '743e9f79bcd8358bd4ddaa2f83d34cfeeb85a56b',
    '948e144d57206b46d11e3450917be4b09dc9a004',
}


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE).decode().strip()


def blob_id(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main(root):
    if not (root / '.git').exists():
        raise ValueError('FredPreview worktree missing')
    origin = git(root, 'remote', 'get-url', 'origin')
    if not origin.rstrip('/').endswith(('DieselHawk/BPFCoBrain', 'DieselHawk/BPFCoBrain.git')):
        raise ValueError('Unexpected repository origin')
    path = root / RELATIVE
    if not path.is_file():
        raise ValueError('Preview renderer missing; no files changed')
    old_id = git(root, 'hash-object', '--', RELATIVE)
    fresh = subprocess.check_output(['git', '-C', str(root), 'show', 'FETCH_HEAD:' + RELATIVE])
    new_id = blob_id(fresh)
    if old_id == new_id:
        print('Preview renderer already current; reload the browser.')
        return
    if old_id not in KNOWN_OLD:
        raise ValueError(f'Unreviewed renderer change {old_id}; no files changed')
    backup = Path(tempfile.mkdtemp(prefix='fred-preview-view-')) / 'super_brain_3d.html'
    previous = path.read_bytes()
    backup.write_bytes(previous)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as staged:
        staged.write(fresh)
        staged_path = Path(staged.name)
    try:
        os.replace(staged_path, path)
        if blob_id(path.read_bytes()) != new_id:
            raise RuntimeError('Renderer byte verification failed')
    except Exception:
        path.write_bytes(previous)
        raise
    print(f'Preview HTML updated; reload http://127.0.0.1:5002/super. Earlier HTML: {backup}')


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
