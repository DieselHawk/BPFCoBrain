"""Project one connection ledger into the verified graph."""
import json
from pathlib import Path

AGENTS = {'Kai_Legal', 'Bob_Finance', 'Neo_Sales', 'Cindy_Secretary'}


def _key(value):
    return str(value).replace('\\', '/').casefold()


def add_role_edges(graph, live):
    path = Path(live) / 'Brain' / 'Executive' / 'connection_ledger.json'
    try:
        ledger = json.loads(path.read_text(encoding='utf-8-sig'))
        if ledger.get('schema') != 1 or not isinstance(ledger.get('entries'), list):
            raise ValueError('Unknown ledger schema')
    except (OSError, ValueError) as exc:
        graph.setdefault('stats', {})['connection_ledger_error'] = str(exc)[:100]
        return graph
    nodes, links = graph.get('nodes', []), graph.get('links', [])
    ids = {str(node.get('id')) for node in nodes if isinstance(node, dict)}
    by_path = {}
    for node in nodes:
        if isinstance(node, dict):
            for value in [node.get('path'), *(node.get('aliases') or [])]:
                if isinstance(value, str) and value:
                    by_path.setdefault(_key(value), set()).add(str(node.get('id')))
    counts = {'proposed': 0, 'source_checked': 0, 'user_confirmed': 0, 'rejected': 0,
              'skipped': 0}
    seen = {(str(edge.get('source')), str(edge.get('target')), edge.get('relationship'))
            for edge in links if isinstance(edge, dict)}
    for entry in ledger['entries']:
        if not isinstance(entry, dict):
            continue
        status, agent = entry.get('status'), entry.get('agent')
        if status not in counts or agent not in AGENTS:
            counts['skipped'] += 1
            continue
        counts[status] += 1
        basis = entry.get('basis')
        if status not in {'source_checked', 'user_confirmed'}:
            continue
        if basis == 'manual_node':
            source = entry.get('node_id')
        else:
            source_path = entry.get('source_file')
            if not isinstance(source_path, str):
                counts['skipped'] += 1
                continue
            try:
                stat = Path(source_path).stat()
                expected = [entry.get('source_mtime_ns'), entry.get('source_size')]
                if expected != [stat.st_mtime_ns, stat.st_size]:
                    counts['skipped'] += 1
                    continue
            except OSError:
                counts['skipped'] += 1
                continue
            matched = by_path.get(_key(source_path), set())
            source = next(iter(matched)) if len(matched) == 1 else None
        target = 'agent:' + agent
        if source not in ids or target not in ids:
            counts['skipped'] += 1
            continue
        relationship = ('ledger_confirmed' if status == 'user_confirmed' else
                        'domain_suggestion')
        edge_key = (source, target, relationship)
        if edge_key in seen:
            continue
        seen.add(edge_key)
        links.append({'source': source, 'target': target, 'relationship': relationship,
                      'strength': 0.8 if status == 'user_confirmed' else 0.6,
                      'unresolved': False, 'role_verified': status == 'source_checked',
                      'user_confirmed': status == 'user_confirmed',
                      'evidence_terms': entry.get('evidence_terms', [])[:10]})
    graph.setdefault('stats', {})['connection_status'] = counts
    graph['stats']['resolved_links'] = sum(1 for edge in links if not edge.get('unresolved'))
    return graph
