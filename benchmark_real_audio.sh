#!/bin/bash
# GPU Benchmark with proper WSL CUDA library path

cd /mnt/c/code/scribe

# Use WSL's CUDA libraries instead of Python package's
export LD_LIBRARY_PATH="/usr/lib/wsl/lib:$LD_LIBRARY_PATH"

python3 << 'EOF'
import time
import torch
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

print(f"PyTorch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print()

audio_file = 'data/audio/recording_20251130_152711.wav'
print(f'Loading: {audio_file}')
audio, sr = sf.read(audio_file)
duration = len(audio) / sr
print(f'Duration: {duration:.1f}s @ {sr}Hz\n')

if sr != 16000:
    from scipy import signal
    audio = signal.resample(audio, int(len(audio) * 16000 / sr))

audio = audio.astype(np.float32)

# CPU Baseline
print('='*60)
print('CPU BASELINE (int8 quantization)')
print('='*60)
model_cpu = WhisperModel('distil-medium.en', device='cpu', compute_type='int8', download_root='models')
start = time.time()
segments_cpu, _ = model_cpu.transcribe(audio, beam_size=5, language='en', vad_filter=True)
result_cpu = list(segments_cpu)
time_cpu = time.time() - start
text_cpu = ' '.join([s.text for s in result_cpu]).strip()
print(f'Time: {time_cpu:.2f}s')
print(f'Speed: {duration/time_cpu:.1f}x realtime')
print(f'Segments: {len(result_cpu)}')
print(f'Text: {text_cpu[:100]}...\n')

# GPU Acceleration
print('='*60)
print('GPU ACCELERATION (float16 precision)')
print('='*60)
try:
    model_gpu = WhisperModel('distil-medium.en', device='cuda', compute_type='float16', download_root='models')
    
    # Warmup
    print('Warming up GPU...')
    _ = list(model_gpu.transcribe(audio[:16000*2], beam_size=1))
    
    start = time.time()
    segments_gpu, _ = model_gpu.transcribe(audio, beam_size=5, language='en', vad_filter=True)
    result_gpu = list(segments_gpu)
    time_gpu = time.time() - start
    text_gpu = ' '.join([s.text for s in result_gpu]).strip()
    
    print(f'Time: {time_gpu:.2f}s')
    print(f'Speed: {duration/time_gpu:.1f}x realtime')
    print(f'Segments: {len(result_gpu)}')
    print(f'Text: {text_gpu[:100]}...\n')
    
    # Comparison
    speedup = time_cpu / time_gpu
    time_saved = time_cpu - time_gpu
    
    print('='*60)
    print('🎯 PERFORMANCE SUMMARY')
    print('='*60)
    print(f'CPU:  {duration/time_cpu:.1f}x realtime  ({time_cpu:.2f}s)')
    print(f'GPU:  {duration/time_gpu:.1f}x realtime  ({time_gpu:.2f}s)')
    print(f'\n🚀 GPU Speedup: {speedup:.1f}x faster')
    print(f'⏱️  Time Saved: {time_saved:.2f}s on {duration:.1f}s audio\n')
    
    print('💡 Projection for 60s audio:')
    print(f'   CPU:  {60/duration*time_cpu:.1f}s')
    print(f'   GPU:  {60/duration*time_gpu:.1f}s')
    print(f'   Savings: {60/duration*(time_cpu-time_gpu):.1f}s')
    
except Exception as e:
    print(f'⚠️  GPU Error: {e}')
    print('Transcription will fall back to CPU automatically in the app.')

EOF
