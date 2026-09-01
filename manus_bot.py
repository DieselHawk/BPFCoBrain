"""BOB - Manus contextual answerer.

Queries the BPFCoBrain vault, retrieves context from Gmail + OneDrive,
and returns contextual answers using Claude.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import anthropic

from query_cli import VaultIndexer
from gmail_hunt import GmailHunter
from ondrive_hunt import OneDriveHunter
from obsidian_writer import ObsidianWriter


class BOBManus:
    """BOB - The contextual answerer for Manus platform.
    
    Integrates BPFCoBrain knowledge base with Gmail + OneDrive context
    to provide intelligent, context-aware responses.
    """
    
    def __init__(
        self,
        vault_path: str = None,
        credentials_file: str = "credentials.json",
        token_file: str = "token.json",
        onedrive_token_file: str = "onedrive_token.json",
        onedrive_client_id: str = None,
        anthropic_key: str = None,
    ):
        """Initialize BOB Manus.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_file: Google OAuth credentials JSON
            token_file: Google token cache
            onedrive_token_file: OneDrive token cache
            onedrive_client_id: Azure client ID (uses env var if not set)
            anthropic_key: Claude API key (uses env var if not set)
        """
        self.vault_path = Path(vault_path or Path.cwd() / "Brain")
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.onedrive_token_file = onedrive_token_file
        self.onedrive_client_id = onedrive_client_id
        
        # Initialize indexer
        self.indexer = None
        self.gmail = None
        self.ondrive = None
        self.client = None
        
        # Track initialization state
        self.errors = []
        self._init_components()
    
    def _init_components(self):
        """Initialize all components, catching errors."""
        # Initialize vault indexer
        try:
            if self.vault_path.exists():
                self.indexer = VaultIndexer(str(self.vault_path))
                self.indexer.index_vault()
            else:
                self.errors.append(f"Vault path not found: {self.vault_path}")
        except Exception as e:
            self.errors.append(f"Vault indexer error: {e}")
        
        # Initialize Gmail
        try:
            if Path(self.credentials_file).exists():
                self.gmail = GmailHunter(self.credentials_file, self.token_file)
            else:
                self.errors.append(f"Google credentials not found: {self.credentials_file}")
        except Exception as e:
            self.errors.append(f"Gmail init error: {e}")
        
        # Initialize OneDrive
        try:
            self.ondrive = OneDriveHunter(self.onedrive_token_file, self.onedrive_client_id)
        except Exception as e:
            self.errors.append(f"OneDrive init error: {e}")
        
        # Initialize Claude
        try:
            api_key = anthropic_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                self.errors.append("ANTHROPIC_API_KEY not set")
            else:
                self.client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            self.errors.append(f"Claude init error: {e}")
    
    def is_ready(self) -> bool:
        """Check if all components are initialized."""
        return all([self.indexer, self.client]) and len(self.errors) == 0
    
    def answer(
        self,
        query: str,
        include_gmail: bool = True,
        include_ondrive: bool = True,
        context_depth: int = 2,
    ) -> Dict:
        """Answer a query using BPFCoBrain context + Gmail + OneDrive.
        
        Args:
            query: Question to answer
            include_gmail: Include Gmail context
            include_ondrive: Include OneDrive context
            context_depth: Vault traversal depth
            
        Returns:
            {
                "query": str,
                "answer": str,
                "sources": [str],
                "context_used": Dict,
                "model": str,
                "usage": Dict,
                "errors": [str]
            }
        """
        if not self.is_ready():
            return {
                "query": query,
                "answer": "BOB not ready: " + "; ".join(self.errors),
                "sources": [],
                "context_used": {},
                "model": "claude-3-5-sonnet-20241022",
                "usage": {"input_tokens": 0, "output_tokens": 0},
                "errors": self.errors
            }
        
        # Step 1: Query the brain vault
        brain_context = self.indexer.query(query, depth=context_depth) if self.indexer else {}
        
        # Step 2: Get Gmail context if requested and available
        gmail_evidence = []
        if include_gmail and self.gmail:
            try:
                gmail_results = self.gmail.hunt_keywords([query])
                for msg_id, _ in list(gmail_results.items())[:3]:  # Top 3 results
                    msg = self.gmail.read_message(msg_id)
                    gmail_evidence.append({
                        "source": "Gmail",
                        "subject": msg.get("subject", ""),
                        "from": msg.get("from", ""),
                        "body": msg.get("body", "")[:1000],
                    })
            except Exception as e:
                pass  # Silently skip if Gmail unavailable
        
        # Step 3: Get OneDrive context if requested and available
        ondrive_evidence = []
        if include_ondrive and self.ondrive:
            try:
                ondrive_results = self.ondrive.hunt_files([query])
                for file_id, file_info in list(ondrive_results.items())[:3]:
                    content = self.ondrive.read_text(file_id, file_info.get("mimeType"))
                    ondrive_evidence.append({
                        "source": "OneDrive",
                        "name": file_info.get("name", ""),
                        "content": content[:1000],
                    })
            except Exception as e:
                pass  # Silently skip if OneDrive unavailable
        
        # Step 4: Build context strings
        brain_notes = ""
        if self.indexer and brain_context.get("context"):
            brain_notes = "\n\n".join([
                f"## {title}\n{self.indexer.notes[title].content[:500]}"
                for title in list(brain_context.get("context", {}).keys())[:5]
            ])
        
        gmail_context_str = "\n\n".join([
            f"**Gmail:** {e['subject']}\nFrom: {e['from']}\n{e['body']}"
            for e in gmail_evidence
        ])
        
        ondrive_context_str = "\n\n".join([
            f"**OneDrive:** {e['name']}\n{e['content']}"
            for e in ondrive_evidence
        ])
        
        # Step 5: Build prompts
        system_prompt = """You are BOB, a contextual answerer for legal case management.
You have access to:
- BPFCoBrain vault (case notes and documents)
- Gmail correspondence
- OneDrive case files

Provide clear, factual answers grounded in evidence.
Always cite which source(s) your answer comes from.
If information is not in the context, clearly state that."""

        user_prompt = f"""Query: {query}

=== BRAIN VAULT ===
{brain_notes[:2000] or "(No vault notes found)"}

=== GMAIL ===
{gmail_context_str[:2000] or "(No Gmail results)"}

=== ONDRIVE ===
{ondrive_context_str[:2000] or "(No OneDrive results)"}

Answer based on the context above, citing sources."""

        # Step 6: Get Claude response
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            
            answer_text = message.content[0].text
            
            # Extract sources
            sources = []
            if self.indexer and brain_context.get("context"):
                sources.extend(list(brain_context["context"].keys()))
            sources.extend([e["subject"] for e in gmail_evidence])
            sources.extend([e["name"] for e in ondrive_evidence])
            
            return {
                "query": query,
                "answer": answer_text,
                "sources": sources,
                "context_used": {
                    "brain_notes": len(brain_context.get("context", {})),
                    "gmail_messages": len(gmail_evidence),
                    "ondrive_files": len(ondrive_evidence),
                },
                "model": "claude-3-5-sonnet-20241022",
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                },
                "errors": []
            }
        
        except Exception as e:
            return {
                "query": query,
                "answer": f"Error getting response: {str(e)}",
                "sources": [],
                "context_used": {},
                "model": "claude-3-5-sonnet-20241022",
                "usage": {"input_tokens": 0, "output_tokens": 0},
                "errors": [str(e)]
            }
    
    def answer_batch(self, queries: List[str], **kwargs) -> List[Dict]:
        """Answer multiple queries."""
        return [self.answer(q, **kwargs) for q in queries]


def cli_main():
    """Simple CLI for testing BOB."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python manus_bot.py <query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    print("\n🧠 BOB Manus Contextual Answerer")
    print("=" * 60)
    print(f"Query: {query}\n")
    
    bob = BOBManus()
    result = bob.answer(query)
    
    print("ANSWER:")
    print("-" * 60)
    print(result["answer"])
    print("-" * 60)
    print(f"\nSources: {', '.join(result['sources'][:5])}")
    print(f"Tokens used: {result['usage']['input_tokens']} input, {result['usage']['output_tokens']} output")


if __name__ == "__main__":
    cli_main()
