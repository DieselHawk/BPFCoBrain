
--- LISTENING PORTS ---
PS C:\BPFCo\BPFCoBrain> Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
>>     Where-Object { $_.LocalPort -in 5000,5001,11434 } |
>>     Select-Object LocalAddress,LocalPort,OwningProcess

LocalAddress LocalPort OwningProcess
------------ --------- -------------
127.0.0.1        11434          9904
127.0.0.1         5001          5884


PS C:\BPFCo\BPFCoBrain>
PS C:\BPFCo\BPFCoBrain> Write-Host "`n--- GIT ---" -ForegroundColor Yellow

--- GIT ---
PS C:\BPFCo\BPFCoBrain> git status --short
 M Brain/Executive/queue.json
 M __pycache__/vault-indexer.cpython-314.pyc
?? Brain/Executive/LinkRepair/check_graph_target.py
PS C:\BPFCo\BPFCoBrain> git branch --show-current
main
PS C:\BPFCo\BPFCoBrain> git log -1 --oneline
87bcd73 (HEAD -> main, origin/main, origin/HEAD) fix: exclude template placeholder links from unresolved graph
PS C:\BPFCo\BPFCoBrain>
PS C:\BPFCo\BPFCoBrain> Write-Host "`n--- TOP-LEVEL APP FILES ---" -ForegroundColor Yellow

--- TOP-LEVEL APP FILES ---
PS C:\BPFCo\BPFCoBrain> Get-ChildItem -File |
>>     Where-Object { $_.Name -match 'app|launch|dashboard|avatar|fred|server|runtime|ollama|omni' } |
>>     Select-Object Name,Length,LastWriteTime

Name                   Length LastWriteTime
----                   ------ -------------
agent_runtime.py         4140 2026/09/19 23:39:29
approval_gate.py         6235 2026/09/20 11:04:34
brain-dashboard.py       2086 2026/09/18 11:09:01
ceo_dashboard.py        15487 2026/09/20 11:13:42
ceo_dashboard.py.bak     7789 2026/09/15 16:45:38
dashboard.html          25251 2026/09/20 10:39:44
dashboard.html.bak      18219 2026/09/02 09:17:16
dashboard.html.v01.bak  20020 2026/09/20 09:35:06
launch-bob.bat           1651 2026/09/01 14:09:01
launch-brain.bat          267 2026/09/10 16:24:07
launch_app.py            1707 2026/09/15 16:39:29
OMNIROUTE-GUIDE.md       3643 2026/07/30 12:43:35
omniroute.py            12357 2026/09/18 10:36:18


PS C:\BPFCo\BPFCoBrain>
PS C:\BPFCo\BPFCoBrain> Write-Host "`n=== END SNAPSHOT ===" -ForegroundColor Cyan

=== END SNAPSHOT ===
