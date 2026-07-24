#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Query CLI - Query your brain"""

import sys, json, argparse, re
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

@dataclass
class Note:
    path: str
    title: str
    content: str
    folder: str = None
    links: List[str] = None
    word_count: int = 0

class VaultIndexer:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.notes: Dict[str, Note] = {}
        self.graph: Dict[str, Set[str]] = {}
        
    def index_vault(self):
        for md_file in self.vault_path.rglob("*.md"):
            if "/.obsidian" in str(md_file):
                continue
            self._index_file(md_file)
        self._build_graph()
    
    def _index_file(self, file_path: Path):
        try:
            content = file_path.read_text(encoding="utf-8")
            title = file_path.stem
            folder = file_path.parent.name
            links = self._extract_links(content)
            note = Note(path=str(file_path.relative_to(self.vault_path)), title=title, content=content, folder=folder, links=links, word_count=len(content.split()))
            self.notes[title] = note
        except:
            pass
    
    def _extract_links(self, content: str):
        return [m.split("|")[0] for m in re.findall(r"\[\[([^\]]+)\]\]", content)]
    
    def _build_graph(self):
        for title, note in self.notes.items():
            self.graph[title] = set()
            for link in note.links:
                link_clean = link.strip()
                if link_clean in self.notes:
                    self.graph[title].add(link_clean)
                else:
                    for nt in self.notes:
                        if nt.lower() == link_clean.lower():
                            self.graph[title].add(nt)
                            break
    
    def query(self, keyword: str, depth: int = 1):
        matches = [t for t, n in self.notes.items() if keyword.lower() in t.lower() or keyword.lower() in n.content.lower()]
        if not matches:
            return {"status": "no_matches"}
        context = {}
        self._build_context(matches[0], context, set(), depth)
        return {"status": "success", "primary": matches[0], "total_matches": len(matches), "context": context}
    
    def _build_context(self, note_title: str, context: Dict, visited: Set, depth: int):
        if depth <= 0 or note_title in visited:
            return
        visited.add(note_title)
        note = self.notes[note_title]
        context[note_title] = {"title": note.title, "folder": note.folder, "links": list(self.graph.get(note_title, set()))}
        for linked in list(self.graph.get(note_title, set()))[:3]:
            if linked not in visited:
                self._build_context(linked, context, visited, depth - 1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--format", default="claude", choices=["json", "claude"])
    args = parser.parse_args()
    
    indexer = VaultIndexer(str(Path.home() / "Documents" / "Obsidian Vault"))
    indexer.index_vault()
    result = indexer.query(args.query, depth=min(args.depth, 3))
    
    if args.format == "json":
        print(json.dumps(result, indent=2))
    elif result["status"] == "success":
        print("=== BRAIN CONTEXT ===\n")
        for nt in result["context"]:
            note = indexer.notes[nt]
            print(f"# {nt}\n{note.content}\n\n---\n")
