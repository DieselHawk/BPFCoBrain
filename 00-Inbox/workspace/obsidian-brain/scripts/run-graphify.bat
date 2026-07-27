@echo off
REM Graphify Runner for Obsidian Brain
REM Usage: run-graphify.bat [path] [options]

set GRAPHIFY_VENV=C:\Users\Jaques\Documents\kimi\workspace\.graphify-venv\Scripts
set "PATH=%GRAPHIFY_VENV%;%PATH%"

if "%~1"=="" (
    echo Usage: run-graphify.bat [path] [options]
    echo.
    echo Examples:
    echo   run-graphify.bat ./raw              -- Extract knowledge graph from raw/
    echo   run-graphify.bat ./raw --obsidian   -- Export to Obsidian vault
    echo   run-graphify.bat ./raw --code-only  -- Code-only extraction (no LLM)
    echo.
    echo For full options, run: graphify --help
    exit /b 1
)

graphify extract %*
