"""
GPU Performance Test - Quick validation of GPU acceleration
Runs automatically when Scribe starts with GPU enabled
"""
import logging
import time
import torch
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

def quick_gpu_test():
    """
    Quick GPU performance test to verify acceleration is working.
    Returns: dict with test results or None if GPU not available
    """
    if not torch.cuda.is_available():
        logger.info("GPU not available - skipping performance test")
        return None
    
    try:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        logger.info(f"🎮 GPU Detected: {gpu_name} ({gpu_memory:.1f}GB)")
        logger.info("Running quick performance test...")
        
        # Quick matrix multiplication test (simulates Whisper computation)
        size = 1024
        device = torch.device("cuda")
        
        # CPU baseline
        a_cpu = torch.randn(size, size)
        b_cpu = torch.randn(size, size)
        
        start = time.time()
        _ = torch.mm(a_cpu, b_cpu)
        cpu_time = time.time() - start
        
        # GPU test
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
        
        logger.info(f"✅ GPU Performance Test Complete")
        logger.info(f"   CPU: {cpu_time*1000:.2f}ms")
        logger.info(f"   GPU: {gpu_time*1000:.2f}ms")
        logger.info(f"   🚀 Speedup: {speedup:.1f}x faster")
        
        return {
            "gpu_name": gpu_name,
            "gpu_memory_gb": gpu_memory,
            "cpu_time_ms": cpu_time * 1000,
            "gpu_time_ms": gpu_time * 1000,
            "speedup": speedup
        }
        
    except Exception as e:
        logger.warning(f"GPU performance test failed: {e}")
        logger.info("Will fall back to CPU transcription")
        return None

def log_gpu_status(device, compute_type):
    """
    Log GPU status in user-friendly format.
    Called by transcription_engine after device detection.
    """
    if device == "cuda":
        logger.info("="*60)
        logger.info("⚡ GPU ACCELERATION ACTIVE")
        logger.info("="*60)
        logger.info(f"Device: {device}")
        logger.info(f"Compute Type: {compute_type}")
        logger.info(f"Expected Performance: 5-10x faster than CPU")
        logger.info(f"")
        logger.info(f"💡 Benefits:")
        logger.info(f"   • Near-instant transcription (<5s audio)")
        logger.info(f"   • Real-time processing for longer recordings")
        logger.info(f"   • Can use larger/more accurate models")
        logger.info("="*60)
        
        # Run quick performance test
        test_result = quick_gpu_test()
        if test_result:
            logger.info(f"")
            logger.info(f"Your GPU: {test_result['gpu_name']}")
            logger.info(f"Memory: {test_result['gpu_memory_gb']:.1f}GB")
            logger.info(f"Compute Speedup: {test_result['speedup']:.1f}x")
        
        logger.info("="*60)
    else:
        logger.info("="*60)
        logger.info("CPU TRANSCRIPTION MODE")
        logger.info("="*60)
        logger.info(f"Device: {device}")
        logger.info(f"Compute Type: {compute_type}")
        logger.info(f"")
        logger.info(f"💡 To enable GPU acceleration (5-10x faster):")
        logger.info(f"   1. Ensure you have an NVIDIA GPU")
        logger.info(f"   2. Install PyTorch: pip install torch --index-url https://download.pytorch.org/whl/cu121")
        logger.info(f"   3. Restart Scribe")
        logger.info(f"   4. See GPU_QUICKSTART.md for details")
        logger.info("="*60)

if __name__ == "__main__":
    # Quick standalone test
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    if torch.cuda.is_available():
        log_gpu_status("cuda", "float16")
    else:
        log_gpu_status("cpu", "int8")
