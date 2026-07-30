class ObsidianWriter:
    def __init__(self, vault_path):
        self.vault_path = vault_path

    def append_to_evidence(self, evidence_list):
        with open(f"{self.vault_path}/Evidence.md", "a") as f:
            for item in evidence_list:
                f.write(f"- {item}\n")
