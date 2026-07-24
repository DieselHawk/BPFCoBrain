@echo off
REM Brain Desktop Launcher - One-click access to your knowledge vault

cd /d "C:\Users\Jaques\Documents\Obsidian Vault"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

REM Run the desktop app
python brain-desktop.py

pause
