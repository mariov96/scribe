import sys
print("Testing faster-whisper GPU load...")

try:
    from faster_whisper import WhisperModel
    print("Creating model on CUDA...")
    model = WhisperModel("tiny", device="cuda", compute_type="float16", download_root="models")
    print("Model loaded successfully on CUDA!")
except Exception as e:
    print(f"CUDA failed: {e}")
    print("\nTrying CPU fallback...")
    try:
        model = WhisperModel("tiny", device="cpu", compute_type="int8", download_root="models")
        print("Model loaded successfully on CPU!")
    except Exception as e2:
        print(f"CPU also failed: {e2}")
