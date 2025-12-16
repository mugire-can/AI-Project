@echo off
cd /d "%~dp0"
python huntrix_game.py
if errorlevel 1 (
    echo.
    echo ERROR: Game failed to run
    pause
)
