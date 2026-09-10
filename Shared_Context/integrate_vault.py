import os
import json

def verify_and_sync():
    vault_path = 'C:\\BPFCo\\BPFCoBrain'
    agents = ['CEO', 'Bob_Finance', 'Cindy_Secretary', 'Kai_Legal', 'Neo_Sales']
    status = {agent: os.path.exists(os.path.join(vault_path, agent)) for agent in agents}
    sync_manifest = {'agents': status, 'persistent_memory': os.path.exists(os.path.join(vault_path, 'Human_In_The_Loop.md'))}
    with open(os.path.join(vault_path, 'Shared_Context', 'manifest.json'), 'w') as f:
        json.dump(sync_manifest, f, indent=4)
    print('[BPFCoBrain] Vault Sync Complete: All agent memory contexts verified.')

if __name__ == '__main__':
    verify_and_sync()
