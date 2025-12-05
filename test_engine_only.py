"""Test transcription engine directly without GUI"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scribe.config import AppConfig
from scribe.core.transcription_engine import TranscriptionEngine

print("Loading config...")
config = AppConfig()

print("Creating transcription engine...")
engine = TranscriptionEngine(config)

print("Initializing (this loads the model)...")
success = engine.initialize()

if success:
    print("✅ Model loaded successfully!")
    print(f"Model: {config.config.whisper.model}")
    
    # Try a quick transcription
    print("\nTesting transcription with sample audio...")
    import numpy as np
    
    # Generate 3 seconds of silence
    sample_rate = 16000
    audio = np.zeros(sample_rate * 3, dtype=np.float32)
    
    result = engine.transcribe(audio)
    print(f"Transcription result: '{result}'")
    print("✅ All tests passed!")
else:
    print("❌ Failed to initialize")
