from pathlib import Path


class ObsidianWriter:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)

    def append_to_evidence(self, evidence_list):
        self.vault_path.mkdir(parents=True, exist_ok=True)
        evidence_file = self.vault_path / "Evidence.md"
        with evidence_file.open("a", encoding="utf-8") as output:
            for item in evidence_list:
                output.write(f"\n{item}\n\n---\n")
