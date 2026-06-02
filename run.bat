@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "VENV_ACTIVATE=%SCRIPT_DIR%venv\Scripts\activate.bat"
set "MAIN_SCRIPT=%SCRIPT_DIR%main.py"

if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment not found at %VENV_ACTIVATE%
    echo Please create it with:  python -m venv venv
    pause
    exit /b 1
)

call "%VENV_ACTIVATE%"

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found after activating the virtual environment.
    echo Please ensure Python is installed and the venv is set up correctly.
    pause
    exit /b 1
)

if not exist "%MAIN_SCRIPT%" (
    echo ERROR: main.py not found at %MAIN_SCRIPT%
    pause
    exit /b 1
)

echo Starting Beta Testing App...
python "%MAIN_SCRIPT%"

if errorlevel 1 (
    echo.
    echo Application exited with an error. See above for details.
    pause
)

endlocal
