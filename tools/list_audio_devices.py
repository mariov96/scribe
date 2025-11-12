#!/usr/bin/env python3
"""
Utility script to list available audio input devices.

Usage:
    python tools/list_audio_devices.py
"""

import sounddevice as sd


def main():
    devices = sd.query_devices()
    default_input = sd.default.device[0]

    print("🎤 Available input devices:")
    print("-" * 60)
    for idx, device in enumerate(devices):
        if device["max_input_channels"] <= 0:
            continue
        marker = " (default)" if idx == default_input else ""
        print(
            f"[{idx:>3}] {device['name']}{marker}\n"
            f"      max channels: {device['max_input_channels']}, "
            f"default sample rate: {device['default_samplerate']}"
        )
    print("-" * 60)
    print("Tip: Use the ID in Settings → Audio Device inside Scribe.")


if __name__ == "__main__":
    main()
