import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*60)
print("SCRIBE GPU VERIFICATION")
print("="*60)

# Check Python
print(f"\nPython: {sys.version}")

# Check PyTorch
try:
    import torch
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
except ImportError as e:
    print(f"PyTorch: NOT INSTALLED - {e}")

# Check faster-whisper
try:
    from faster_whisper import WhisperModel
    print(f"faster-whisper: OK")
except ImportError as e:
    print(f"faster-whisper: NOT INSTALLED - {e}")

# Check Scribe modules
try:
    from scribe.core.transcription_engine import TranscriptionEngine
    print(f"Scribe core: OK")
except ImportError as e:
    print(f"Scribe core: {e}")

# Check device detection
print("\n" + "="*60)
print("DEVICE DETECTION TEST")
print("="*60)

try:
    from scribe.config.app_config import AppConfig
    config = AppConfig()
    engine = TranscriptionEngine(config)
    device, compute = engine._detect_best_device()
    print(f"\nDetected Device: {device}")
    print(f"Compute Type: {compute}")
    
    if device == "cuda":
        print("\n✅ GPU ACCELERATION READY!")
        print("   Expected: 5-10x faster transcription")
    else:
        print("\n⚠️  CPU mode (GPU not available)")
except Exception as e:
    print(f"Device detection error: {e}")

print("\n" + "="*60)
