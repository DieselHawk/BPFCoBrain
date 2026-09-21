@echo off
echo [BPFCoBrain] Booting Offline-Hardwired 2D Vault Wrapper...
start /min cmd /c "python C:\BPFCo\BPFCoBrain\brain-dashboard.py"
timeout /t 2 >nul
start msedge.exe --app=http://127.0.0.1:5000 --window-size=1280,800
:network_loop
ping -n 1 8.8.8.8 >nul
if %errorlevel% equ 0 (
    echo [ONLINE DETECTED] Network restored! Triggering live agent runtime...
    start /min cmd /c "python C:\BPFCo\BPFCoBrain\agent_runtime.py"
    exit
)
timeout /t 15 >nul
goto network_loop
