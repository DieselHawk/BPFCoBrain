"""Store agent outcomes in the one shared executive experience directory."""

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import os
import re

class ExperienceSynthesizer:
    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path).resolve()
        self.memory_folder = self.vault_path / "Brain" / "Executive" / "Experience"
        self.memory_folder.mkdir(parents=True, exist_ok=True)

    def synthesize(self, agent_name, task_id, report):
        """Keep one record per agent/task without overwriting older experiences."""
        safe_agent = re.sub(r"[^A-Za-z0-9_-]", "_", str(agent_name))[:48]
        key = hashlib.sha256(f"{agent_name}\0{task_id}".encode("utf-8")).hexdigest()[:16]
        filepath = self.memory_folder / f"EXP_{safe_agent}_{key}.md"
        if filepath.exists():
            return filepath
        timestamp = datetime.now(timezone.utc).isoformat()
        content = (
            f"# Experience Insight: {agent_name}\n"
            f"**Task ID**: {task_id}\n"
            f"**Timestamp**: {timestamp}\n\n"
            f"## Outcome\n{report}\n\n"
            f"---\n"
            f"Tags: #experience #agent_{safe_agent.lower()} #synthesis"
        )
        try:
            # Exclusive create protects a task written by another worker.
            with filepath.open("x", encoding="utf-8") as stream:
                stream.write(content)
            return filepath
        except FileExistsError:
            return filepath
        except OSError as exc:
            print(f"Synthesis failed: {exc}")
            return None
