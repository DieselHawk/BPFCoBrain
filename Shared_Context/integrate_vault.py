import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def verify_and_sync():
    agents = ['CEO', 'Bob_Finance', 'Cindy_Secretary', 'Kai_Legal', 'Neo_Sales']
    status = {agent: (ROOT / agent).is_dir() for agent in agents}
    sync_manifest = {'agents': status, 'persistent_memory': (ROOT / 'Human_In_The_Loop.md').is_file()}
    with (ROOT / 'Shared_Context' / 'manifest.json').open('w', encoding='utf-8') as f:
        json.dump(sync_manifest, f, indent=4)
    print(f'[BPFCoBrain] Vault Sync Complete: agent workspaces checked at {ROOT}.')

if __name__ == '__main__':
    verify_and_sync()
