"""Bounded offline document graph: exact-copy aliases and explicit citations only."""
import hashlib
import os
import shutil
import subprocess
import threading
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

from Dashboard.adapters.note_edges import _key, _targets

MAX_DOCUMENTS = 1000
MAX_DEPTH = 5
MAX_FILE_BYTES = 100_000_000
MAX_HASH_BYTES_PER_REQUEST = 300_000_000
MAX_EXTRACT_PER_REQUEST = 8
MAX_LINKS = 100
MAX_TEXT = 150_000
EXTENSIONS = {'.md', '.txt', '.docx', '.pdf'}
_W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
_hash_cache = {}
_target_cache = {}
_lock = threading.Lock()


def _signature(path):
    stat = path.stat()
    return (stat.st_mtime_ns, stat.st_size)


def _digest(path, signature):
    saved = _hash_cache.get(path)
    if saved and saved[0] == signature:
        return saved[1]
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    if _signature(path) != signature:
        raise OSError('Document changed during hashing')
    digest = h.hexdigest()
    _hash_cache[path] = (signature, digest)
    return digest


def _docx_text(path):
    with zipfile.ZipFile(path) as archive:
        xml = archive.getinfo('word/document.xml')
        if xml.file_size > 4_000_000:
            return ''
        tree = ElementTree.fromstring(archive.read(xml))
        lines = []
        length = 0
        for paragraph in tree.iter(_W + 'p'):
            line = ''.join(n.text or '' for n in paragraph.iter(_W + 't'))
            lines.append(line)
            length += len(line)
            if length >= MAX_TEXT:
                break
        return '\n'.join(lines)[:MAX_TEXT]


def _scanned_pdf_text(path):
    """Optional offline OCR for a bounded scan, used by the resumable catalog."""
    from Brain.Executive.ocr_runtime import installed_tools
    tools = installed_tools()
    if tools is None:
        return ''
    ocr, renderer = tools
    with tempfile.TemporaryDirectory(prefix='bpfco-ocr-') as temp:
        target = str(Path(temp) / 'page')
        try:
            rendered = subprocess.run(
                [renderer, '-f', '1', '-l', '2', '-scale-to', '1600', '-gray', '-png', str(path), target],
                capture_output=True, timeout=30, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ''
        if rendered.returncode:
            return ''
        lines = []
        for image in sorted(Path(temp).glob('page-*.png'))[:2]:
            try:
                result = subprocess.run(
                    [ocr, str(image), 'stdout', '--psm', '3'], capture_output=True,
                    timeout=30, check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                continue
            if result.returncode == 0:
                lines.append(result.stdout.decode('utf-8', errors='replace'))
        return '\n'.join(lines)[:MAX_TEXT]


def _pdf_text(path, ocr=False):
    text = ''
    executable = shutil.which('pdftotext')
    if executable:
        try:
            result = subprocess.run([executable, '-f', '1', '-l', '5', '-enc', 'UTF-8',
                                     str(path), '-'], capture_output=True,
                                    timeout=5, check=False)
            if result.returncode == 0:
                text = result.stdout.decode('utf-8', errors='replace')[:MAX_TEXT]
        except subprocess.TimeoutExpired:
            pass
    if not text.strip():
        try:
            from pypdf import PdfReader
            with path.open('rb') as stream:
                reader = PdfReader(stream, strict=False)
                text = '\n'.join((page.extract_text() or '')[:MAX_TEXT]
                                 for page in reader.pages[:5])[:MAX_TEXT]
        except Exception:
            # Optional PDF readers can fail on encrypted or damaged inputs.
            pass
    if ocr and len(text.strip()) < 40:
        return _scanned_pdf_text(path) or text
    return text or None


def _references(path, signature):
    cached = _target_cache.get(path)
    if cached and cached[0] == signature:
        return cached[1]
    try:
        if path.suffix.lower() == '.docx':
            text = _docx_text(path)
        elif path.suffix.lower() == '.pdf':
            text = _pdf_text(path)
        else:
            text = path.read_text(encoding='utf-8-sig', errors='replace')[:MAX_TEXT]
        if text is None:
            _target_cache[path] = (signature, None)
            return None
        refs = list(_targets(text))[:MAX_LINKS]
    except (OSError, ValueError, zipfile.BadZipFile, ElementTree.ParseError,
            subprocess.TimeoutExpired, KeyError):
        refs = []
    except Exception:
        # Optional PDF readers raise their own errors for malformed or encrypted files.
        refs = []
    _target_cache[path] = (signature, refs)
    return refs


def add_document_edges(graph, root, documents_root=None):
    """One node per confirmed identical file; preserve all cited file paths."""
    from Brain.Executive.source_registry import documents_root as configured_documents
    source = documents_root or configured_documents()
    if not source:
        return graph
    folder = Path(source).expanduser().resolve()
    if not folder.is_dir():
        graph.setdefault('stats', {})['document_error'] = 'Documents folder unavailable'
        return graph
    nodes, edges = graph.get('nodes'), graph.get('links')
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return graph
    with _lock:
        return _build(graph, folder)


def _build(graph, folder):
    nodes, edges = graph['nodes'], graph['links']
    files = []
    source_files_seen = 0
    source_snapshot = hashlib.sha256()
    source_incomplete = False
    for current, directories, names in os.walk(folder, followlinks=False):
        depth = len(Path(current).relative_to(folder).parts)
        if depth >= MAX_DEPTH and directories:
            source_incomplete = True
        directories[:] = sorted(d for d in directories if not (Path(current) / d).is_symlink()) if depth < MAX_DEPTH else []
        for name in sorted(names):
            if len(files) >= MAX_DOCUMENTS:
                source_incomplete = True
                break
            path = Path(current) / name
            try:
                signature = _signature(path)
                source_files_seen += 1
                source_snapshot.update((str(path.relative_to(folder)).casefold()
                                        + ':' + str(signature) + '\n').encode('utf-8', 'replace'))
                if (path.suffix.lower() not in EXTENSIONS or path.is_symlink()
                        or signature[1] > MAX_FILE_BYTES or not path.resolve().is_relative_to(folder)):
                    continue
                files.append((path, signature))
            except OSError:
                continue
        if len(files) >= MAX_DOCUMENTS:
            break
    by_size = defaultdict(list)
    for path, signature in files:
        by_size[signature[1]].append((path, signature))
    confirmed = defaultdict(list)
    hash_budget = MAX_HASH_BYTES_PER_REQUEST
    unverified = 0
    changed_during_scan = 0
    for path, signature in files:
        try:
            if _signature(path) != signature:
                changed_during_scan += 1
                unverified += 1
                confirmed['unverified:' + _key(path)].append((path, signature))
                continue
        except OSError:
            changed_during_scan += 1
            unverified += 1
            confirmed['unverified:' + _key(path)].append((path, signature))
            continue
        if len(by_size[signature[1]]) == 1:
            identity = 'single:' + _key(path)
        elif path in _hash_cache and _hash_cache[path][0] == signature:
            identity = 'sha256:' + _hash_cache[path][1]
        elif hash_budget >= signature[1]:
            try:
                identity = 'sha256:' + _digest(path, signature)
                hash_budget -= signature[1]
            except OSError:
                identity = 'unverified:' + _key(path)
                unverified += 1
                changed_during_scan += 1
        else:
            identity = 'unverified:' + _key(path)
            unverified += 1
        confirmed[identity].append((path, signature))
    by_path = {_key(n.get('path')): str(n['id']) for n in nodes
               if isinstance(n, dict) and n.get('path')}
    canonical = []
    new_nodes = 0
    for members in confirmed.values():
        path, signature = members[0]
        aliases = [str(item[0]) for item in members]
        node_id = by_path.get(_key(path))
        if node_id is None:
            relative = path.relative_to(folder).as_posix()
            node_id = 'document:' + relative.casefold()
            if any(str(n.get('id')) == node_id for n in nodes if isinstance(n, dict)):
                continue
            nodes.append({'id': node_id, 'label': path.stem, 'title': path.stem,
                          'path': str(path), 'aliases': aliases,
                          'duplicate_count': len(aliases),
                          'folder': 'Documents / ' + str(path.relative_to(folder).parent),
                          'word_count': 0, 'connection_count': 0,
                          'links': [], 'content': '', 'frontmatter': {}})
            new_nodes += 1
        else:
            for node in nodes:
                if isinstance(node, dict) and str(node.get('id')) == node_id:
                    node['aliases'] = list(dict.fromkeys([str(node['path'])] + aliases))
                    node['duplicate_count'] = len(node['aliases'])
                    break
        for alias in aliases:
            by_path[_key(alias)] = node_id
        canonical.append((path, signature, node_id))
    # A directory is a recorded storage relationship, not a claim that
    # its contents discuss one another. Preserve the real hierarchy only.
    folder_ids = {}
    folder_links = 0

    def ensure_folder(path):
        nonlocal folder_links
        relative = path.relative_to(folder).as_posix()
        identifier = 'document-folder:' + relative.casefold()
        if path in folder_ids:
            return folder_ids[path]
        folder_ids[path] = identifier
        nodes.append({'id': identifier,
                      'label': path.name,
                      'title': str(path),
                      'path': str(path),
                      'folder': 'Documents / Folders',
                      'kind': 'document_folder',
                      'word_count': 0, 'connection_count': 0,
                      'links': [], 'content': '', 'frontmatter': {}})
        if path != folder:
            parent_id = ensure_folder(path.parent)
            edges.append({'source': identifier, 'target': parent_id,
                          'relationship': 'folder_within',
                          'strength': 1, 'unresolved': False})
            folder_links += 1
        return identifier

    for path, _, source_id in canonical:
        folder_id = ensure_folder(path.parent)
        edges.append({'source': source_id, 'target': folder_id,
                      'relationship': 'stored_in',
                      'strength': 1, 'unresolved': False})
        folder_links += 1

    names = defaultdict(set)
    for node in nodes:
        if isinstance(node, dict) and node.get('path'):
            stem = Path(str(node['path'])).stem.casefold()
            if stem:
                names[stem].add(str(node['id']))
    seen = {(str(e.get('source')), str(e.get('target'))) for e in edges if isinstance(e, dict)}
    added = 0
    extracted = 0
    pending = 0
    unavailable = 0
    for path, signature, source_id in canonical:
        cached = _target_cache.get(path)
        if not cached or cached[0] != signature:
            if extracted >= MAX_EXTRACT_PER_REQUEST:
                pending += 1
                continue
            extracted += 1
        refs = _references(path, signature)
        if refs is None:
            unavailable += 1
            continue
        for target, relationship in refs:
            target = target.strip()
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            candidates = set()
            if _key(candidate) in by_path:
                candidates.add(by_path[_key(candidate)])
            if not candidates and '/' not in target and '\\' not in target:
                candidates = names.get(Path(target).stem.casefold(), set())
            if len(candidates) != 1:
                continue
            target_id = next(iter(candidates))
            if source_id == target_id or (source_id, target_id) in seen:
                continue
            seen.add((source_id, target_id))
            edges.append({'source': source_id, 'target': target_id,
                          'relationship': 'document_' + relationship,
                          'strength': 1, 'unresolved': False})
            added += 1
    stats = graph.setdefault('stats', {})
    stats['document_sources'] = len(files)
    stats['source_files_seen'] = source_files_seen
    stats['source_snapshot'] = source_snapshot.hexdigest()[:16]
    stats['source_scanned_at'] = datetime.now(timezone.utc).isoformat()
    stats['source_scan_incomplete'] = source_incomplete
    stats['source_changed_during_scan'] = changed_during_scan
    stats['document_nodes'] = new_nodes
    stats['document_folder_nodes'] = len(folder_ids)
    stats['document_folder_links'] = folder_links
    stats['exact_duplicate_groups'] = sum(len(members) > 1 for members in confirmed.values())
    stats['exact_duplicate_files'] = sum(len(members) for members in confirmed.values() if len(members) > 1)
    stats['document_duplicates_suppressed'] = len(files) - len(confirmed)
    stats['document_unverified_hashes'] = unverified
    stats['document_links'] = added
    stats['document_pending'] = pending
    stats['document_extractor_unavailable'] = unavailable
    stats['resolved_links'] = sum(1 for edge in edges if isinstance(edge, dict) and not edge.get('unresolved'))
    return graph
