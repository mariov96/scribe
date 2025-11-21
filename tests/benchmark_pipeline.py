import time
import numpy as np
import soundfile as sf
import tempfile
import os
from pathlib import Path

def benchmark_pipeline():
    print("Running Audio Pipeline Benchmark...")
    
    # Setup dummy audio (5 seconds of silence/noise at 16kHz)
    duration = 5
    sr = 16000
    audio_data = np.random.uniform(-0.5, 0.5, int(duration * sr)).astype(np.float32)
    
    iterations = 50
    
    # --- Scenario A: The "Before" State (Disk I/O Heavy) ---
    start_time = time.time()
    for _ in range(iterations):
        # 1. AudioRecorder saves to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f1:
            sf.write(f1.name, audio_data, sr)
            temp_path1 = f1.name
            
        # 2. AudioRecorder reads bytes to emit
        with open(temp_path1, 'rb') as f:
            data_bytes = f.read()
            
        # 3. TranscriptionEngine saves bytes to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f2:
            f2.write(data_bytes)
            temp_path2 = f2.name
            
        # 4. Preprocessing reads file
        data, _ = sf.read(temp_path2)
        
        # (Simulate processing)
        processed = data * 0.9 
        
        # 5. Preprocessing writes new file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f3:
            sf.write(f3.name, processed, sr)
            temp_path3 = f3.name
            
        # Cleanup
        os.unlink(temp_path1)
        os.unlink(temp_path2)
        os.unlink(temp_path3)
        
    duration_old = time.time() - start_time
    avg_old = (duration_old / iterations) * 1000
    
    print(f"\n[Old Pipeline] Disk-based:")
    print(f"  Total time ({iterations} runs): {duration_old:.4f}s")
    print(f"  Avg latency per run: {avg_old:.2f}ms")

    # --- Scenario B: The "After" State (In-Memory) ---
    start_time = time.time()
    for _ in range(iterations):
        # 1. AudioRecorder emits array directly (0 cost copy)
        data = audio_data.copy()
        
        # 2. TranscriptionEngine receives array
        # 3. Preprocessing (In-memory)
        processed = data * 0.9
        
        # (No disk I/O)
        
    duration_new = time.time() - start_time
    avg_new = (duration_new / iterations) * 1000
    
    print(f"\n[New Pipeline] In-Memory:")
    print(f"  Total time ({iterations} runs): {duration_new:.4f}s")
    print(f"  Avg latency per run: {avg_new:.2f}ms")
    
    # --- Results ---
    improvement = duration_old / duration_new if duration_new > 0 else 0
    print(f"\n>>> Speedup Factor: {improvement:.1f}x")
    print(f">>> Latency Reduction: {avg_old - avg_new:.2f}ms per transcription")

if __name__ == "__main__":
    benchmark_pipeline()