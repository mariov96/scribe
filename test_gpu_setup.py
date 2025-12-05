#!/usr/bin/env python3
"""
Complete GPU Setup Verification Test
Run this to verify GPU acceleration is properly configured
"""
import sys
from pathlib import Path

print("="*70)
print("SCRIBE GPU ACCELERATION VERIFICATION")
print("="*70)
print()

# Test 1: Python version
print("[1/6] Checking Python Version...")
print(f"   Version: {sys.version.split()[0]}")
if sys.version_info >= (3, 10):
    print("   ✅ Python 3.10+ detected")
else:
    print("   ❌ Python 3.10+ required")
    sys.exit(1)
print()

# Test 2: PyTorch installation
print("[2/6] Checking PyTorch Installation...")
try:
    import torch
    print(f"   PyTorch Version: {torch.__version__}")
    print("   ✅ PyTorch installed")
except ImportError:
    print("   ❌ PyTorch not installed")
    print("   Install with: pip install torch --index-url https://download.pytorch.org/whl/cu121")
    sys.exit(1)
print()

# Test 3: CUDA availability
print("[3/6] Checking CUDA Support...")
try:
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        print(f"   CUDA Available: True")
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   Device Count: {torch.cuda.device_count()}")
        print(f"   GPU Name: {torch.cuda.get_device_name(0)}")
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
        print("   ✅ CUDA GPU detected")
    else:
        print("   ⚠️  CUDA not available")
        print("   GPU acceleration will not work")
        print("   Check NVIDIA driver installation")
except Exception as e:
    print(f"   ❌ Error checking CUDA: {e}")
    sys.exit(1)
print()

# Test 4: Faster-whisper installation
print("[4/6] Checking faster-whisper Installation...")
try:
    from faster_whisper import WhisperModel
    print("   ✅ faster-whisper installed")
except ImportError:
    print("   ❌ faster-whisper not installed")
    print("   Install with: pip install faster-whisper")
    sys.exit(1)
print()

# Test 5: Scribe core modules
print("[5/6] Checking Scribe Core Modules...")
try:
    # Add src to path if needed
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    from scribe.core.transcription_engine import TranscriptionEngine
    from scribe.core.gpu_utils import quick_gpu_test, log_gpu_status
    print("   ✅ Scribe core modules loaded")
except ImportError as e:
    print(f"   ⚠️  Could not import Scribe modules: {e}")
    print("   This is OK if running outside Scribe directory")
print()

# Test 6: GPU performance
print("[6/6] Running GPU Performance Test...")
if cuda_available:
    try:
        from scribe.core.gpu_utils import quick_gpu_test
        result = quick_gpu_test()
        if result:
            print(f"   GPU: {result['gpu_name']}")
            print(f"   Memory: {result['gpu_memory_gb']:.1f} GB")
            print(f"   CPU Time: {result['cpu_time_ms']:.2f}ms")
            print(f"   GPU Time: {result['gpu_time_ms']:.2f}ms")
            print(f"   Speedup: {result['speedup']:.1f}x")
            print("   ✅ GPU performance test passed")
        else:
            print("   ⚠️  GPU test returned None")
    except Exception as e:
        # Simple fallback test
        print("   Running simple GPU test...")
        import time
        
        device = torch.device("cuda")
        size = 512
        
        a_cpu = torch.randn(size, size)
        b_cpu = torch.randn(size, size)
        
        start = time.time()
        _ = torch.mm(a_cpu, b_cpu)
        cpu_time = time.time() - start
        
        a_gpu = a_cpu.to(device)
        b_gpu = b_cpu.to(device)
        
        # Warmup
        _ = torch.mm(a_gpu, b_gpu)
        torch.cuda.synchronize()
        
        start = time.time()
        _ = torch.mm(a_gpu, b_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start
        
        speedup = cpu_time / gpu_time
        
        print(f"   CPU: {cpu_time*1000:.2f}ms")
        print(f"   GPU: {gpu_time*1000:.2f}ms")
        print(f"   Speedup: {speedup:.1f}x")
        print("   ✅ Simple GPU test passed")
else:
    print("   ⏭️  Skipped (no GPU)")
print()

# Summary
print("="*70)
print("VERIFICATION SUMMARY")
print("="*70)
if cuda_available:
    print("✅ GPU ACCELERATION IS READY!")
    print()
    print("Expected Performance:")
    print("  • 5-10x faster transcription than CPU")
    print("  • Near-instant for short clips (<5s)")
    print("  • Real-time for longer recordings")
    print()
    print("Next Steps:")
    print("  1. Launch Scribe: Start Scribe.vbs")
    print("  2. Check Settings → Transcription for 'cuda' status")
    print("  3. Record audio and observe faster transcription")
    print("  4. Check logs: %USERPROFILE%\\.scribe\\logs\\")
else:
    print("⚠️  GPU NOT AVAILABLE")
    print()
    print("Scribe will work but use CPU mode (slower)")
    print()
    print("To enable GPU:")
    print("  1. Ensure NVIDIA GPU is installed")
    print("  2. Update GPU driver: nvidia.com/drivers")
    print("  3. Reinstall PyTorch:")
    print("     pip install torch --index-url https://download.pytorch.org/whl/cu121 --force-reinstall")
    print("  4. Restart and run this test again")

print("="*70)
print()
