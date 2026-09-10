import subprocess
import time
import os

print('[BPFCoBrain] Booting full system interface...')

# 1. Integrate context
subprocess.run(['python', r'C:\BPFCo\BPFCoBrain\Shared_Context\integrate_vault.py'])

# 2. Start Python Web/AI Dashboard in background
subprocess.Popen(['python', r'C:\BPFCo\BPFCoBrain\brain-dashboard.py'])

# 3. Launch TheBrain 15 Desktop App
os.system(r'start "" "C:\Users\Jaques\Desktop\TheBrain 15.lnk"')

# 4. Launch Dashboard in Google Chrome
time.sleep(2)
subprocess.Popen([r'C:\Program Files\Google\Chrome\Application\chrome.exe', 'http://localhost:5000'])

print('[BPFCoBrain] TheBrain 15 and Chrome Dashboard launched successfully!')
