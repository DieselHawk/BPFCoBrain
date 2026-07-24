#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniRoute - File ingestion and multi-model token orchestrator"""

import sys, os, json, re, argparse, hashlib
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import anthropic

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class FileImporter:
    """Import computer files into vault"""
    
    SUPPORTED_TYPES = {'.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml', '.rs', '.go', '.java', '.cpp', '.c', '.h'}
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.import_log = self.vault_path / ".imports.json"
        self.imports = self._load_imports()
    
    def _load_imports(self) -> Dict:
        if self.import_log.exists():
            return json.loads(self.import_log.read_text())
        return {}
    
    def _save_imports(self):
        self.import_log.write_text(json.dumps(self.imports, indent=2))
    
    def import_file(self, source_path: str, category: str = "03-References") -> bool:
        """Import a file into vault"""
        source = Path(source_path)
        
        if not source.exists():
            print(f"Error: {source_path} not found")
            return False
        
        if source.suffix not in self.SUPPORTED_TYPES:
            print(f"Unsupported file type: {source.suffix}")
            return False
        
        # Generate unique hash
        content_hash = hashlib.md5(source.read_bytes()).hexdigest()[:8]
        
        # Check if already imported
        if content_hash in self.imports:
            print(f"Already imported: {source.name}")
            return False
        
        # Create destination
        dest_folder = self.vault_path / category
        dest_folder.mkdir(exist_ok=True)
        
        dest_name = f"{source.stem}-{content_hash}.md"
        dest_path = dest_folder / dest_name
        
        # Format file as markdown with metadata
        content = source.read_text(encoding='utf-8', errors='ignore')
        markdown = f"""---
type: imported
source: {source_path}
imported: {datetime.now().isoformat()}
file_type: {source.suffix}
---

# {source.name}

**Original:** `{source_path}`

## Content

```{source.suffix[1:]}
{content}
```
"""
        
        dest_path.write_text(markdown)
        
        # Log import
        self.imports[content_hash] = {
            "source": str(source_path),
            "dest": str(dest_path),
            "imported": datetime.now().isoformat(),
            "file_type": source.suffix
        }
        self._save_imports()
        
        print(f"✓ Imported: {source.name} → {dest_name}")
        return True

class TokenManager:
    """Manage token usage across models"""
    
    MODELS = {
        "claude-3-5-sonnet": {"name": "Claude 3.5 Sonnet", "tokens": 200000},
        "claude-3-opus": {"name": "Claude 3 Opus", "tokens": 200000},
        "claude-3-haiku": {"name": "Claude 3 Haiku", "tokens": 200000},
    }
    
    def __init__(self):
        self.usage_log = Path.home() / ".omniroute_usage.json"
        self.usage = self._load_usage()
    
    def _load_usage(self) -> Dict:
        if self.usage_log.exists():
            return json.loads(self.usage_log.read_text())
        return {model: {"used": 0, "reset": datetime.now().isoformat()} for model in self.MODELS}
    
    def _save_usage(self):
        self.usage_log.write_text(json.dumps(self.usage, indent=2))
    
    def get_available_model(self) -> str:
        """Get next available model with remaining tokens"""
        for model, config in self.MODELS.items():
            used = self.usage[model]["used"]
            available = config["tokens"] - used
            if available > 10000:  # Keep 10k buffer
                return model
        return None
    
    def log_usage(self, model: str, tokens: int):
        """Log token usage"""
        if model not in self.usage:
            self.usage[model] = {"used": 0, "reset": datetime.now().isoformat()}
        self.usage[model]["used"] += tokens
        self._save_usage()
        
        print(f"[{model}] +{tokens} tokens (total: {self.usage[model]['used']})")
    
    def get_status(self) -> Dict:
        """Get token status for all models"""
        status = {}
        for model, config in self.MODELS.items():
            used = self.usage[model]["used"]
            available = config["tokens"] - used
            status[model] = {
                "used": used,
                "available": available,
                "percent": int((used / config["tokens"]) * 100)
            }
        return status
    
    def reset_daily(self):
        """Reset daily token limits"""
        for model in self.usage:
            self.usage[model]["used"] = 0
            self.usage[model]["reset"] = datetime.now().isoformat()
        self._save_usage()
        print("✓ Daily token limits reset")

class OmniRouter:
    """Main orchestrator"""
    
    def __init__(self, vault_path: str):
        self.importer = FileImporter(vault_path)
        self.token_manager = TokenManager()
        self.vault_path = vault_path
    
    def ingest_files(self, file_list: List[str], category: str = "03-References"):
        """Ingest multiple files"""
        print(f"[*] Ingesting {len(file_list)} files into {category}...")
        success = 0
        for file_path in file_list:
            if self.importer.import_file(file_path, category):
                success += 1
        print(f"✓ {success}/{len(file_list)} files imported")
    
    def query_with_fallback(self, query: str, context: str = "", max_retries: int = 3):
        """Query with automatic model fallback"""
        client = anthropic.Anthropic()
        
        for attempt in range(max_retries):
            model = self.token_manager.get_available_model()
            
            if not model:
                print("ERROR: No models with available tokens!")
                return None
            
            print(f"\n[*] Using {model} (attempt {attempt + 1}/{max_retries})")
            
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Context:\n{context}\n\nQuery: {query}"
                        }
                    ]
                )
                
                # Log usage
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
                self.token_manager.log_usage(model, tokens_used)
                
                return response.content[0].text
            
            except anthropic.RateLimitError:
                print(f"[!] {model} token limit reached, trying next...")
                continue
            except Exception as e:
                print(f"[!] Error with {model}: {e}")
                continue
        
        return None
    
    def status(self):
        """Show token status"""
        print("\n=== OmniRoute Token Status ===\n")
        status = self.token_manager.get_status()
        for model, stats in status.items():
            bar = "█" * (stats["percent"] // 5) + "░" * (20 - stats["percent"] // 5)
            print(f"{model}")
            print(f"  [{bar}] {stats['percent']}% ({stats['used']:,}/{stats['used'] + stats['available']:,})")
            print(f"  Available: {stats['available']:,} tokens\n")

def main():
    parser = argparse.ArgumentParser(description="OmniRoute - File ingestion & multi-model orchestrator")
    subparsers = parser.add_subparsers(dest="command")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import files into brain")
    import_parser.add_argument("files", nargs="+", help="File paths to import")
    import_parser.add_argument("--category", default="03-References", help="Vault category")
    
    # Status command
    subparsers.add_parser("status", help="Show token usage status")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query with automatic fallback")
    query_parser.add_argument("query", help="Query text")
    query_parser.add_argument("--context", default="", help="Additional context")
    
    # Reset command
    subparsers.add_parser("reset", help="Reset daily token limits")
    
    args = parser.parse_args()
    vault_path = str(Path.home() / "Documents" / "Obsidian Vault")
    router = OmniRouter(vault_path)
    
    if args.command == "import":
        router.ingest_files(args.files, args.category)
    elif args.command == "status":
        router.status()
    elif args.command == "query":
        result = router.query_with_fallback(args.query, args.context)
        if result:
            print(f"\n=== Response ===\n{result}")
    elif args.command == "reset":
        router.token_manager.reset_daily()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
