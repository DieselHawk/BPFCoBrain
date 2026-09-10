@echo off
echo [BPFCoBrain] Initializing Persistent Agent State...
powershell -NoExit -Command "Get-ChildItem -Path 'C:\BPFCo\BPFCoBrain' -Recurse | Select-Object FullName, Length, LastWriteTime"
echo [BPFCoBrain] Agent context active. All systems persistent.
pause
