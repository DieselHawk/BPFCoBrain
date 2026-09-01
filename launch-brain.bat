@echo off
REM Brain Desktop Launcher - Self-Healing Edition
REM This script finds the vault even if moved, and ensures everything is ready

setlocal enabledelayedexpansion

REM Check the folder containing this launcher first.
if exist "%~dp0brain-desktop.py" (
    set "VAULT_PATH=%~dp0"
    goto :found_vault
)

REM Look for the vault by checking for the signature file
for /d %%D in ("%USERPROFILE%\Documents\*") do (
    if exist "%%D\.vault-index.json" (
        set "VAULT_PATH=%%D"
        goto :found_vault
    )
)

REM Try common locations
if exist "%USERPROFILE%\Documents\Obsidian Vault\.vault-index.json" (
    set "VAULT_PATH=%USERPROFILE%\Documents\Obsidian Vault"
    goto :found_vault
)

REM If not found, ask user
echo.
echo 🧠 Brain Desktop Launcher
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ❌ Could not find Obsidian Vault
echo.
echo Where is your vault located?
echo Example: C:\Users\YourName\Documents\Obsidian Vault
echo.
set /p "VAULT_PATH=Enter vault path: "

if not exist "!VAULT_PATH!\.vault-index.json" (
    echo.
    echo ❌ Not a valid vault. Missing .vault-index.json
    pause
    exit /b 1
)

:found_vault
REM Now in vault directory
cd /d "!VAULT_PATH!"

echo.
echo 🧠 Brain Desktop Launcher
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📍 Vault: !VAULT_PATH!
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    echo.
    echo Install from: https://www.python.org/downloads/
    echo Make sure to check "Add to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check required libraries
python -c "import PySimpleGUI" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing PySimpleGUI...
    pip install PySimpleGUI -q
    if errorlevel 1 (
        echo ❌ Failed to install PySimpleGUI
        pause
        exit /b 1
    )
    echo ✅ PySimpleGUI installed
    echo.
)

REM Create an index when it is missing.
if not exist ".vault-index.json" (
    echo ⚠️  Creating vault index...
    python vault-indexer.py >nul 2>&1
    if errorlevel 1 (
        echo ❌ Failed to create vault index
        pause
        exit /b 1
    )
    echo ✅ Index created
    echo.
)

REM Launch the app!
echo 🚀 Launching Brain Desktop...
echo.

python brain-desktop.py

exit /b 0
