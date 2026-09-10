@echo off
echo ===================================================
echo [BPFCoBrain] Booting Complete Executive Agent Suite
echo ===================================================

echo [1/3] Indexing Vault Memory & Context...
powershell -Command "python 'C:\BPFCo\BPFCoBrain\Shared_Context\integrate_vault.py'"

echo [2/3] Launching Background Web Dashboard & API Server...
start /min cmd /c "python C:\BPFCo\BPFCoBrain\brain-dashboard.py"

echo [3/3] Launching Obsidian Visual Interface...
powershell -Command "Start-Process 'obsidian://open?vault=BPFCoBrain'"

echo ===================================================
echo [BPFCoBrain] System Fully Operational!
echo ===================================================
timeout /t 3
