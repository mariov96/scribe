@echo off
REM Scribe Repository Setup Script for Windows
REM Run this after cloning to initialize your development environment

echo 🎯 Setting up Scribe development environment...
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% detected

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating data directories...
if not exist "data" mkdir data
if not exist "data\audio" mkdir data\audio
if not exist "data\logs" mkdir data\logs
if not exist "data\analytics" mkdir data\analytics
if not exist "data\sessions" mkdir data\sessions
if not exist "data\metrics" mkdir data\metrics
if not exist "docs\screenshots" mkdir docs\screenshots
if not exist "models" mkdir models

echo.
echo ✅ Setup complete!
echo.
echo 🚀 Quick start:
echo    1. Activate venv: venv\Scripts\activate
echo    2. Run Scribe: python run_scribe.py
echo.
echo 📖 See DEPLOYMENT_GUIDE.md for publishing to GitHub
pause
