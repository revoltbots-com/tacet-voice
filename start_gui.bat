@echo off
echo Starting Tacet GUI...
echo.

REM Check if virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment and run GUI
call venv\Scripts\activate.bat
python stt_gui.py

REM Keep window open if there's an error
if errorlevel 1 pause
