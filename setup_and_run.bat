@echo off
setlocal enabledelayedexpansion

title Beta Testing Manager - First Time Setup

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "REQ_FILE=%SCRIPT_DIR%requirements.txt"
set "MAIN_SCRIPT=%SCRIPT_DIR%main.py"

echo.
echo ===============================================
echo  Beta Testing Manager - First Time Setup
echo ===============================================
echo.
echo This will create a local Python environment, install the
echo app requirements, and then start the app.
echo.

if not exist "%MAIN_SCRIPT%" (
    echo ERROR: main.py was not found.
    echo Make sure you run this file from the Beta Testing App folder.
    pause
    exit /b 1
)

if not exist "%REQ_FILE%" (
    echo ERROR: requirements.txt was not found.
    pause
    exit /b 1
)

if exist "%VENV_PY%" (
    echo Found existing virtual environment.
    goto install_requirements
)

echo Creating virtual environment...
call :find_python
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found.
    echo Install Python 3.11 or newer from https://www.python.org/downloads/
    echo During install, tick "Add python.exe to PATH".
    pause
    exit /b 1
)

%PYTHON_CMD% -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo.
    echo ERROR: Could not create the virtual environment.
    pause
    exit /b 1
)

:install_requirements
echo.
echo Installing requirements...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo ERROR: Could not upgrade pip.
    pause
    exit /b 1
)

"%VENV_PY%" -m pip install -r "%REQ_FILE%"
if errorlevel 1 (
    echo.
    echo ERROR: Requirement installation failed.
    echo Check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Starting Beta Testing Manager...
"%VENV_PY%" "%MAIN_SCRIPT%"
if errorlevel 1 (
    echo.
    echo The app exited with an error. See the message above for details.
    pause
    exit /b 1
)

exit /b 0

:find_python
set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3"
        exit /b 0
    )
)

where python >nul 2>nul
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
        exit /b 0
    )
)

exit /b 1
