import sounddevice as sd

def list_devices():
    print("Available Audio Devices:")
    print("-" * 60)
    print(f"{'ID':<4} {'Name':<40} {'Channels':<10} {'Sample Rate'}")
    print("-" * 60)
    
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        # Filter for input devices (microphones)
        if device['max_input_channels'] > 0:
            print(f"{i:<4} {device['name']:<40} {device['max_input_channels']:<10} {device['default_samplerate']}")

if __name__ == "__main__":
    list_devices()
