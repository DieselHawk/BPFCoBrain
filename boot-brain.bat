@echo off
echo [BPFCoBrain] Booting Full Executive Agent Suite (Offline-Hardwired)...
start /min cmd /c "python C:\BPFCo\BPFCoBrain\ceo_dashboard.py"
timeout /t 3 >nul
start msedge.exe --app=http://127.0.0.1:5001 --window-size=1280,800
:network_loop
ping -n 1 8.8.8.8 >nul
if %errorlevel% equ 0 (
    echo [ONLINE DETECTED] Network restored! Triggering live agent runtime...
    start /min cmd /c "python C:\BPFCo\BPFCoBrain\agent_runtime.py"
    exit
)
timeout /t 15 >nul
goto network_loop
