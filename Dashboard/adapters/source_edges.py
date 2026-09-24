"""Connect task evidence and report citations to verified document nodes."""

import json
from pathlib import Path


def add_source_edges(graph, root):
    nodes, edges = graph['nodes'], graph['links']
    paths = {}
    for node in nodes:
        for path in [node.get('path'), *(node.get('aliases') or [])]:
            if path:
                paths.setdefault(str(path).replace('\\', '/').casefold(), set()).add(str(node['id']))
    added = 0
    for kind, field in (('tasks', 'evidence'), ('reports', 'sources')):
        for file in sorted((Path(root) / 'Brain' / 'Executive' / kind).glob('*.json')):
            try:
                record = json.loads(file.read_text(encoding='utf-8-sig'))
            except (OSError, ValueError):
                continue
            source = ('task:' if kind == 'tasks' else 'report:') + str(record.get('task_id', ''))
            if not any(node['id'] == source for node in nodes):
                continue
            seen = set()
            for item in record.get(field, [])[:100]:
                path = item.get('path') if isinstance(item, dict) else item
                if not isinstance(path, str):
                    continue
                matches = paths.get(path.replace('\\', '/').casefold(), set())
                if len(matches) != 1:
                    continue
                target = next(iter(matches))
                if target in seen or target == source:
                    continue
                seen.add(target)
                if any(e.get('source') == source and e.get('target') == target for e in edges):
                    continue
                edges.append({'source': source, 'target': target,
                              'relationship': 'evidence' if kind == 'tasks' else 'cites',
                              'strength': 1, 'unresolved': False})
                added += 1
    graph['stats']['document_source_links'] = added
    graph['stats']['resolved_links'] += added
    return graph
