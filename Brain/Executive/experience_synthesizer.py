from pathlib import Path
from datetime import datetime, timezone
import json
import os

ROOT = Path(__file__).resolve().parent

class ExperienceSynthesizer:
    """
    Translates agent task outcomes into structured knowledge nodes.
    """
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.memory_folder = vault_path / "Brain" / "Executive" / "Experience"
        self.memory_folder.mkdir(parents=True, exist_ok=True)

    def synthesize(self, agent_name, task_id, report):
        """
        Analyze a report and create a knowledge node if an insight is found.
        """
        # In a full implementation, this would call an LLM to extract 
        # 'Permanent Knowledge' vs 'Transient Data'.
        # For now, we create a structured experience log.
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
        filename = f"EXP_{agent_name}_{timestamp}.md"
        filepath = self.memory_folder / filename
        
        content = (
            f"# Experience Insight: {agent_name}\n"
            f"**Task ID**: {task_id}\n"
            f"**Timestamp**: {datetime.now(timezone.utc).isoformat()}\n\n"
            f"## Outcome\n{report}\n\n"
            f"---\n"
            f"Tags: #experience #agent_{agent_name.lower()} #synthesis"
        )
        
        try:
            filepath.write_text(content, encoding="utf-8")
            return filepath
        except Exception as e:
            print(f"Synthesis failed: {e}")
            return None
