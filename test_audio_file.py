"""Test transcription of a recorded audio file"""
import sys
sys.path.insert(0, 'src')

from pathlib import Path
from scribe.config.config_manager import ConfigManager
from scribe.core.transcription_engine import TranscriptionEngine

print("=" * 80)
print("Testing audio file transcription")
print("=" * 80)

# Initialize transcription engine
config = ConfigManager()
engine = TranscriptionEngine(config)

if not engine.initialize():
    print("❌ Failed to initialize transcription engine")
    sys.exit(1)

print("✅ Transcription engine initialized")

# Test the most recent audio file
audio_file = Path("data/audio/recording_20251204_131111.wav")
if not audio_file.exists():
    print(f"❌ Audio file not found: {audio_file}")
    sys.exit(1)

print(f"\n📁 Testing file: {audio_file}")
print(f"   Size: {audio_file.stat().st_size / 1024:.1f} KB")

# Test transcription
result = engine.transcribe(str(audio_file))

print("\n" + "=" * 80)
if result and result.text:
    print(f"✅ Transcription successful!")
    print(f"   Text: {result.text}")
    print(f"   Duration: {result.duration:.2f}s")
    if result.confidence:
        print(f"   Confidence: {result.confidence:.2%}")
else:
    print("❌ No speech detected or transcription failed")
    if result:
        print(f"   Result object: {result}")
        print(f"   Text: '{result.text}'")
        print(f"   Duration: {result.duration}")
print("=" * 80)
