@echo off
echo ============================================================
echo Scribe GPU Setup - Python 3.12 + PyTorch CUDA Installation
echo ============================================================
echo.

REM Check if Python 3.12 is installed
where python312 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python 3.12 found
    goto :install_pytorch
)

REM Check common Python 3.12 locations
if exist "C:\Python312\python.exe" (
    echo [OK] Python 3.12 found at C:\Python312
    set PYTHON312=C:\Python312\python.exe
    goto :install_pytorch
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo [OK] Python 3.12 found at %LOCALAPPDATA%\Programs\Python\Python312
    set PYTHON312=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    goto :install_pytorch
)

echo.
echo ============================================================
echo Python 3.12 is required for PyTorch GPU support
echo ============================================================
echo.
echo PyTorch does not yet support Python 3.13
echo.
echo Please install Python 3.12:
echo   1. Download from: https://www.python.org/downloads/release/python-3129/
echo   2. Run installer and check "Add to PATH"
echo   3. Run this script again
echo.
echo Direct download link:
echo   https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe
echo.
pause
exit /b 1

:install_pytorch
echo.
echo Installing PyTorch with CUDA 12.1 support...
echo This may take 5-10 minutes (downloading ~2GB)
echo.

if defined PYTHON312 (
    "%PYTHON312%" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
) else (
    python312 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyTorch installation failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Verifying GPU Detection...
echo ============================================================

if defined PYTHON312 (
    "%PYTHON312%" -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}' if torch.cuda.is_available() else 'No GPU')"
) else (
    python312 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}' if torch.cuda.is_available() else 'No GPU')"
)

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Update Scribe to use Python 3.12
echo   2. Launch Scribe and enjoy 5-10x faster transcription!
echo.
pause
