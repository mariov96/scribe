#!/usr/bin/env python3
"""
GPU Performance Benchmark
Compares CPU vs GPU transcription performance
"""

import time
import torch
import numpy as np
from pathlib import Path
from faster_whisper import WhisperModel

def benchmark_device(device, compute_type, model_size="distil-medium.en", duration=30):
    """Benchmark transcription on specified device."""
    print(f"\n{'='*60}")
    print(f"Testing: {device.upper()} with {compute_type}")
    print(f"{'='*60}")
    
    # Load model
    print(f"Loading model: {model_size}...")
    start = time.time()
    model = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type,
        download_root="models"
    )
    load_time = time.time() - start
    print(f"✅ Model loaded in {load_time:.2f}s")
    
    # Generate synthetic audio (simulate recording)
    sample_rate = 16000
    audio_duration = duration
    print(f"\nGenerating {audio_duration}s test audio...")
    audio = np.random.randn(sample_rate * audio_duration).astype(np.float32) * 0.1
    
    # Warmup run (GPU needs this)
    if device == "cuda":
        print("Warming up GPU...")
        _ = list(model.transcribe(audio[:sample_rate*5], beam_size=1))
    
    # Benchmark transcription
    print(f"\nTranscribing {audio_duration}s audio...")
    start = time.time()
    segments, info = model.transcribe(
        audio,
        beam_size=5,
        language="en",
        vad_filter=True
    )
    
    # Consume generator
    segment_count = sum(1 for _ in segments)
    transcribe_time = time.time() - start
    
    # Calculate metrics
    speed_ratio = audio_duration / transcribe_time
    
    print(f"\n📊 Results:")
    print(f"   Audio Duration: {audio_duration:.1f}s")
    print(f"   Transcription Time: {transcribe_time:.2f}s")
    print(f"   Speed: {speed_ratio:.2f}x realtime")
    print(f"   Segments: {segment_count}")
    
    if device == "cuda":
        memory_used = torch.cuda.max_memory_allocated() / (1024**3)
        print(f"   Peak GPU Memory: {memory_used:.2f} GB")
    
    return {
        "device": device,
        "compute_type": compute_type,
        "load_time": load_time,
        "transcribe_time": transcribe_time,
        "speed_ratio": speed_ratio,
        "audio_duration": audio_duration
    }

def main():
    """Run GPU vs CPU benchmark."""
    print("🚀 Scribe GPU Performance Benchmark")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"GPU: {gpu_name} ({gpu_memory:.1f} GB)")
    
    results = []
    
    # Benchmark CPU
    print("\n" + "="*60)
    print("BASELINE: CPU Performance")
    print("="*60)
    cpu_result = benchmark_device("cpu", "int8", duration=15)
    results.append(cpu_result)
    
    # Benchmark GPU
    if torch.cuda.is_available():
        print("\n" + "="*60)
        print("GPU ACCELERATION TEST")
        print("="*60)
        gpu_result = benchmark_device("cuda", "float16", duration=15)
        results.append(gpu_result)
        
        # Compare
        speedup = gpu_result["speed_ratio"] / cpu_result["speed_ratio"]
        time_saved = cpu_result["transcribe_time"] - gpu_result["transcribe_time"]
        
        print("\n" + "="*60)
        print("🎯 PERFORMANCE COMPARISON")
        print("="*60)
        print(f"\nCPU:  {cpu_result['speed_ratio']:.2f}x realtime  ({cpu_result['transcribe_time']:.2f}s)")
        print(f"GPU:  {gpu_result['speed_ratio']:.2f}x realtime  ({gpu_result['transcribe_time']:.2f}s)")
        print(f"\n✨ GPU Speedup: {speedup:.2f}x faster than CPU")
        print(f"⏱️  Time Saved: {time_saved:.2f}s on 15s audio")
        print(f"\n💡 For 1 minute of audio:")
        print(f"   CPU would take:  {60 / cpu_result['speed_ratio']:.1f}s")
        print(f"   GPU takes:       {60 / gpu_result['speed_ratio']:.1f}s")
        print(f"   Savings:         {60/cpu_result['speed_ratio'] - 60/gpu_result['speed_ratio']:.1f}s")
    else:
        print("\n⚠️  No GPU available for comparison")
    
    print("\n✅ Benchmark complete!")

if __name__ == "__main__":
    main()
