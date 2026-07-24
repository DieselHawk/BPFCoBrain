#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Vault Indexer
Indexes Obsidian vault and provides efficient context extraction for Claude
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, asdict
from datetime import datetime

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

@dataclass
class Note:
    """Represents a single vault note"""
    path: str
    title: str
    content: str
    frontmatter: Dict = None
    links: List[str] = None
    backlinks: List[str] = None
    folder: str = None
    word_count: int = 0

class VaultIndexer:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.notes: Dict[str, Note] = {}
        self.index: Dict[str, List[str]] = {}  # keyword -> [note_titles]
        self.graph: Dict[str, Set[str]] = {}   # note -> connected_notes
        
    def index_vault(self) -> None:
        """Scan and index all markdown files in vault"""
        print(f"📚 Indexing vault: {self.vault_path}")
        
        for md_file in self.vault_path.rglob("*.md"):
            # Skip .obsidian and hidden folders
            if "/.obsidian" in str(md_file) or md_file.name.startswith("."):
                continue
                
            self._index_file(md_file)
        
        self._build_graph()
        print(f"✓ Indexed {len(self.notes)} notes")
    
    def _index_file(self, file_path: Path) -> None:
        """Index a single markdown file"""
        try:
            content = file_path.read_text(encoding="utf-8")
            title = file_path.stem
            folder = file_path.parent.name
            
            # Parse frontmatter
            frontmatter = self._parse_frontmatter(content)
            
            # Extract links [[like-this]]
            links = self._extract_links(content)
            
            note = Note(
                path=str(file_path.relative_to(self.vault_path)),
                title=title,
                content=content,
                frontmatter=frontmatter,
                links=links,
                folder=folder,
                word_count=len(content.split())
            )
            
            self.notes[title] = note
            
        except Exception as e:
            print(f"⚠ Error indexing {file_path}: {e}")
    
    def _parse_frontmatter(self, content: str) -> Dict:
        """Extract YAML frontmatter"""
        if not content.startswith("---"):
            return {}
        
        try:
            parts = content.split("---", 2)
            if len(parts) >= 2:
                lines = parts[1].strip().split("\n")
                fm = {}
                for line in lines:
                    if ":" in line:
                        key, val = line.split(":", 1)
                        fm[key.strip()] = val.strip()
                return fm
        except:
            pass
        return {}
    
    def _extract_links(self, content: str) -> List[str]:
        """Extract internal links [[like-this]]"""
        pattern = r"\[\[([^\]]+)\]\]"
        matches = re.findall(pattern, content)
        return [m.split("|")[0] for m in matches]  # Handle [[link|alias]]
    
    def _build_graph(self) -> None:
        """Build bidirectional graph of note connections"""
        for title, note in self.notes.items():
            self.graph[title] = set()
            
            for link in note.links:
                # Normalize link (remove .md, case-insensitive match)
                link_clean = link.strip()
                
                # Try exact match first
                if link_clean in self.notes:
                    self.graph[title].add(link_clean)
                else:
                    # Try case-insensitive
                    for note_title in self.notes:
                        if note_title.lower() == link_clean.lower():
                            self.graph[title].add(note_title)
                            break
    
    def query(self, keyword: str, depth: int = 1) -> Dict:
        """
        Query vault with intelligent context extraction
        Returns note with connected context up to specified depth
        """
        # Find matching notes
        matches = []
        keyword_lower = keyword.lower()
        
        for title, note in self.notes.items():
            if (keyword_lower in title.lower() or 
                keyword_lower in note.content.lower()):
                matches.append(title)
        
        if not matches:
            return {"status": "no_matches", "keyword": keyword}
        
        # Build context graph
        context = {}
        visited = set()
        
        self._build_context(matches[0], context, visited, depth)
        
        return {
            "status": "success",
            "primary": matches[0],
            "total_matches": len(matches),
            "context": context,
            "token_estimate": self._estimate_tokens(context)
        }
    
    def _build_context(self, note_title: str, context: Dict, visited: Set, depth: int) -> None:
        """Recursively build context graph"""
        if depth <= 0 or note_title in visited:
            return
        
        visited.add(note_title)
        note = self.notes[note_title]
        
        context[note_title] = {
            "title": note.title,
            "folder": note.folder,
            "word_count": note.word_count,
            "links": list(self.graph.get(note_title, set())),
            "preview": note.content[:300] + "..." if len(note.content) > 300 else note.content
        }
        
        # Add connected notes
        for linked in list(self.graph.get(note_title, set()))[:3]:  # Limit to 3 connections
            if linked not in visited:
                self._build_context(linked, context, visited, depth - 1)
    
    def _estimate_tokens(self, context: Dict) -> int:
        """Rough token estimation (4 chars ≈ 1 token)"""
        content_str = json.dumps(context)
        return len(content_str) // 4
    
    def export_index(self, output_path: str) -> None:
        """Export vault index as JSON for external tools"""
        index_data = {
            "timestamp": datetime.now().isoformat(),
            "vault_path": str(self.vault_path),
            "note_count": len(self.notes),
            "notes": {
                title: {
                    "path": note.path,
                    "folder": note.folder,
                    "word_count": note.word_count,
                    "links": note.links,
                    "frontmatter": note.frontmatter
                }
                for title, note in self.notes.items()
            },
            "graph": {k: list(v) for k, v in self.graph.items()}
        }
        
        Path(output_path).write_text(json.dumps(index_data, indent=2))
        print(f"✓ Index exported to {output_path}")
    
    def print_stats(self) -> None:
        """Print vault statistics"""
        total_words = sum(note.word_count for note in self.notes.values())
        total_links = sum(len(note.links) for note in self.notes.values())
        
        print("\n📊 Vault Statistics:")
        print(f"  Notes: {len(self.notes)}")
        print(f"  Total words: {total_words:,}")
        print(f"  Total links: {total_links}")
        print(f"  Avg connections per note: {total_links / max(len(self.notes), 1):.1f}")

def main():
    vault_path = os.path.expanduser("~/Documents/Obsidian Vault")
    
    indexer = VaultIndexer(vault_path)
    indexer.index_vault()
    indexer.print_stats()
    
    # Export index
    index_file = os.path.join(vault_path, ".vault-index.json")
    indexer.export_index(index_file)
    
    # Example query
    print("\n🔍 Example query: 'Concept'")
    result = indexer.query("Concept", depth=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
