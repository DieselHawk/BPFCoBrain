@echo off
echo [BPFCoBrain] Initializing Persistent Agent State...
powershell -Command "Get-ChildItem -Path 'C:\BPFCo\BPFCoBrain' -Recurse | Select-Object FullName, Length, LastWriteTime" > "C:\BPFCo\BPFCoBrain\Shared_Context\vault_startup.log"
echo [BPFCoBrain] Agent context active. All systems persistent.
