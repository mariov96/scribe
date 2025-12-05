"""Real-time audio level monitor to diagnose microphone issues"""
import sounddevice as sd
import numpy as np
import time

device_id = 0
print(f"Monitoring audio levels from device {device_id} (Sound Mapper)")
print("=" * 60)

devices = sd.query_devices()
print(f"Device name: {devices[device_id]['name']}")
print(f"Channels: {devices[device_id]['max_input_channels']}")
print(f"Default sample rate: {devices[device_id]['default_samplerate']}")
print("=" * 60)
print("\nMake some noise! Watching audio levels for 10 seconds...")
print("(You should see numbers changing if microphone is working)\n")

def audio_callback(indata, frames, time_info, status):
    """Called for each audio block"""
    if status:
        print(f"Status: {status}")
    
    # Calculate RMS level
    volume_norm = np.linalg.norm(indata) * 10
    rms = np.sqrt(np.mean(indata**2))
    peak = np.abs(indata).max()
    
    # Show bar graph of level
    bars = int(volume_norm)
    bar_str = "█" * min(bars, 50)
    
    print(f"\rRMS: {rms:8.2f} | Peak: {peak:6.0f} | {bar_str:<50}", end="", flush=True)

# Open stream and listen
try:
    with sd.InputStream(device=device_id, channels=1, samplerate=16000, 
                        callback=audio_callback, blocksize=1024):
        time.sleep(10)
except Exception as e:
    print(f"\n\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Check Windows Sound Settings -> Input -> Device properties")
    print("2. Check microphone volume level (should be 80-100)")
    print("3. Test microphone in Windows Sound Recorder app")
    print("4. Make sure the correct microphone is selected as default")

print("\n\nDone!")
