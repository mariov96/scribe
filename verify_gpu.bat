@echo off
REM GPU Verification Script for Scribe
REM Run this to verify GPU acceleration is working

echo ========================================
echo Scribe GPU Verification
echo ========================================
echo.

REM Check NVIDIA driver
echo [1/4] Checking NVIDIA Driver...
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader >nul 2>&1
if errorlevel 1 (
    echo FAILED: NVIDIA driver not found
    echo Please update your GPU driver from nvidia.com
    echo.
    pause
    exit /b 1
) else (
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
)
echo.

REM Check Python
echo [2/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo FAILED: Python not found
    echo Please install Python from python.org
    echo.
    pause
    exit /b 1
) else (
    python --version
)
echo.

REM Check PyTorch CUDA
echo [3/4] Checking PyTorch CUDA Support...
python -c "import torch; print(f'PyTorch Version: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}'); print(f'GPU Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB' if torch.cuda.is_available() else '')" 2>nul
if errorlevel 1 (
    echo FAILED: PyTorch not installed or CUDA not available
    echo.
    echo To install PyTorch with CUDA support:
    echo pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    echo.
    pause
    exit /b 1
)
echo.

REM Check Scribe configuration
echo [4/4] Checking Scribe Device Detection...
python -c "from src.scribe.core.transcription_engine import TranscriptionEngine; engine = TranscriptionEngine(None); device, compute = engine._detect_best_device(); print(f'Selected Device: {device}'); print(f'Compute Type: {compute}'); print(''); print('SUCCESS: GPU acceleration is ready!' if device == 'cuda' else 'WARNING: Will use CPU-only mode')" 2>nul
if errorlevel 1 (
    echo Note: Full test requires running from Scribe directory
)
echo.

echo ========================================
echo Verification Complete
echo ========================================
echo.
echo Next steps:
echo 1. Launch Scribe using "Start Scribe.vbs"
echo 2. Check Settings - Transcription for device status
echo 3. Status chip should show: "Active: model · cuda · float16"
echo 4. Record audio and observe 5-10x faster transcription
echo.
pause
