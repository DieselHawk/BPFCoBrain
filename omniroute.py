#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniRoute - File ingestion and multi-model token orchestrator"""

import sys, os, json, re, argparse, hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import urllib.request
import urllib.error

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
        
        content_hash = hashlib.md5(source.read_bytes()).hexdigest()[:8]
        
        if content_hash in self.imports:
            print(f"Already imported: {source.name}")
            return False
        
        dest_folder = self.vault_path / category
        dest_folder.mkdir(exist_ok=True)
        
        dest_name = f"{source.stem}-{content_hash}.md"
        dest_path = dest_folder / dest_name
        
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
        
        self.imports[content_hash] = {
            "source": str(source_path),
            "dest": str(dest_path),
            "imported": datetime.now().isoformat(),
            "file_type": source.suffix
        }
        self._save_imports()
        
        print(f"✅ Imported: {source.name} → {dest_name}")
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
    
    def get_available_model(self) -> Optional[str]:
        for model, config in self.MODELS.items():
            used = self.usage[model]["used"]
            available = config["tokens"] - used
            if available > 10000:
                return model
        return None
    
    def log_usage(self, model: str, tokens: int):
        if model not in self.usage:
            self.usage[model] = {"used": 0, "reset": datetime.now().isoformat()}
        self.usage[model]["used"] += tokens
        self._save_usage()
        print(f"[{model}] +{tokens} tokens (total: {self.usage[model]['used']})")
    
    def get_status(self) -> Dict:
        status = {}
        for model, config in self.MODELS.items():
            used = self.usage[model]["used"]
            available = config["tokens"] - used
            status[model] = {
                "used": used,
                "available": available,
                "percent": int((used / config["tokens"]) * 100) if config["tokens"] > 0 else 0
            }
        return status
    
    def reset_daily(self):
        for model in self.usage:
            self.usage[model]["used"] = 0
            self.usage[model]["reset"] = datetime.now().isoformat()
        self._save_usage()
        print("✅ Daily token limits reset")

class OmniRouter:
    """Main orchestrator"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.importer = FileImporter(vault_path)
        self.token_manager = TokenManager()
    
    def ingest_files(self, file_list: List[str], category: str = "03-References"):
        print(f"[*] Ingesting {len(file_list)} files into {category}...")
        success = 0
        for file_path in file_list:
            if self.importer.import_file(file_path, category):
                success += 1
        print(f"✅ {success}/{len(file_list)} files imported")
    
    def query_with_fallback(self, query: str, context: str = "", max_retries: int = 3, persona: str = None):
        """Query the configured model gateway. Local Ollama is preferred."""



        # 1. Persona Injection
        if persona:
            # Search for persona in Brain/Executive/Personas/ relative to repo root
            persona_path = Path("Brain/Executive/Personas") / f"{persona.lower()}.md"
            if persona_path.exists():
                persona_content = persona_path.read_text(encoding='utf-8')
                context = f"SYSTEM PERSONA MANDATE:\n{persona_content}\n\nCONTEXT:\n{context}"
            else:
                print(f"[!] Persona file for {persona} not found at {persona_path}")

        # 2. Local-First Routing (Ollama)
        # Priority: Ollama (local)
        model = os.environ.get("BPFCO_OLLAMA_MODEL", "hermes3:8b")
        url = os.environ.get("BPFCO_OLLAMA_URL", "http://127.0.0.1:11434/api/chat")

        prompt = f"Context:\n{context}\n\nQuery: {query}"
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"num_predict": 512, "temperature": 0.2},
        }).encode("utf-8")

        print(f"\n[*] Routing to local Ollama [{model}]...")

        try:
            request = urllib.request.Request(
                url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
            )
            with urllib.request.urlopen(request, timeout=300) as response:
                result = json.loads(response.read().decode("utf-8"))
            
            answer = result.get("message", {}).get("content", "").strip()
            if answer:
                return answer
        except Exception as exc:
            print(f"[!] Local Ollama error: {type(exc).__name__}: {exc}")
            # Check if user has explicitly disabled all outgoing traffic
            if os.environ.get("BPFCO_OFFLINE") == "1":
                print("[!] BPFCO_OFFLINE is enabled. Blocking cloud fallback.")
                return None



        # 3. Cloud Fallback (Anthropic)
        # ONLY execute if BPFCO_OFFLINE is not set to "1"
        if os.environ.get("BPFCO_OFFLINE") == "1":
            print("[!] BPFCO_OFFLINE is enabled. Cloud fallback is disabled by choice.")
            return None

        try:
            import anthropic
            client = anthropic.Anthropic()
            for attempt in range(max_retries):
                model_cloud = self.token_manager.get_available_model()
                if not model_cloud: return None
                
                print(f"\n[*] Using cloud model {model_cloud} (attempt {attempt + 1}/{max_retries})")
                try:
                    response = client.messages.create(
                        model=model_cloud, max_tokens=1024,
                        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuery: {query}"}]
                    )
                    self.token_manager.log_usage(model_cloud, response.usage.input_tokens + response.usage.output_tokens)
                    return response.content[0].text
                except Exception as e:
                    print(f"[!] Error with {model_cloud}: {e}")
            return None
        except ImportError:
            print("[!] Anthropic library not installed, cloud fallback unavailable.")
            return None

    def status(self):
        print("\n=== OmniRoute Token Status ===\n")
        status = self.token_manager.get_status()
        for model, stats in status.items():
            bar = "█" * (stats["percent"] // 5) + "░" * (20 - stats["percent"] // 5)
            print(f"{model}\n  [{bar}] {stats['percent']}% ({stats['used']:,}/{stats['used'] + stats['available']:,})")

def main():
    parser = argparse.ArgumentParser(description="OmniRoute - File ingestion & multi-model orchestrator")
    subparsers = parser.add_subparsers(dest="command")
    
    import_parser = subparsers.add_parser("import", help="Import files into brain")
    import_parser.add_argument("files", nargs="+", help="File paths to import")
    import_parser.add_argument("--category", default="03-References", help="Vault category")
    
    subparsers.add_parser("status", help="Show token usage status")
    
    query_parser = subparsers.add_parser("query", help="Query with automatic fallback")
    query_parser.add_argument("query", help="Query text")
    query_parser.add_argument("--context", default="", help="Additional context")
    query_parser.add_argument("--persona", default=None, help="Agent persona to use (e.g. Fred, Bob)")
    
    subparsers.add_parser("reset", help="Reset daily token limits")
    
    args = parser.parse_args()
    
    vault_path = Path(__file__).resolve().parent / "Brain"
    router = OmniRouter(str(vault_path))
    
    if args.command == "import":
        router.ingest_files(args.files, args.category)
    elif args.command == "status":
        router.status()
    elif args.command == "query":
        result = router.query_with_fallback(args.query, args.context, persona=args.persona)
        if result:
            print(f"\n=== Response ===\n{result}")
    elif args.command == "reset":
        router.token_manager.reset_daily()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
