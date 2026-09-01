@echo off
REM BOB Manus - Launch script for Windows

echo.
echo 🤖 BOB Manus Contextual Answerer
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Install Python 3.9+ first.
    pause
    exit /b 1
)

REM Check requirements
if not exist requirements.txt (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Install dependencies if needed
echo [*] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
)

REM Menu
:menu
cls
echo.
echo 🤖 BOB Manus Menu
echo ================================
echo.
echo [1] Start API Server (http://localhost:5000)
echo [2] Ask BOB a question
echo [3] Sync Gmail/Drive/OneDrive evidence
echo [4] Open Setup Guide
echo [5] Exit
echo.

set /p choice="Choose (1-5): "

if "%choice%"=="1" goto api_server
if "%choice%"=="2" goto ask_bob
if "%choice%"=="3" goto sync
if "%choice%"=="4" goto setup
if "%choice%"=="5" exit /b 0

echo ❌ Invalid choice
timeout /t 2 >nul
goto menu

:api_server
cls
echo.
echo 🚀 Starting BOB API Server...
echo.
python manus_api.py
goto menu

:ask_bob
cls
echo.
set /p query="Ask BOB (query): "
echo.
python manus_bot.py %query%
echo.
pause
goto menu

:sync
cls
echo.
set /p keywords="Keywords to sync (space-separated): "
echo.
python main.py %keywords%
echo.
pause
goto menu

:setup
cls
echo.
echo Opening MANUS-BOB-SETUP.md...
echo.
start notepad MANUS-BOB-SETUP.md
timeout /t 1 >nul
goto menu
