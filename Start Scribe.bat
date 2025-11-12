@echo off
REM Scribe Launcher - Windows Batch Script
REM Alternative launcher for users who prefer .bat files

cd /d "%~dp0"

REM Try to find Python
set PYTHON_CMD=

REM Check common Python installation paths
if exist "C:\Python313\python.exe" (
    set PYTHON_CMD=C:\Python313\python.exe
) else if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
) else if exist "C:\Python311\python.exe" (
    set PYTHON_CMD=C:\Python311\python.exe
) else (
    REM Try python from PATH
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
    )
)

REM Check if Python was found
if "%PYTHON_CMD%"=="" (
    echo ERROR: Python not found!
    echo Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)

REM Launch Scribe
start "Scribe - The Open Voice Platform" "%PYTHON_CMD%" run_scribe.py

exit /b 0
