"""
Real Audio Recorder using sounddevice
Captures audio from microphone with configurable sample rate and channels.
"""

import logging
import shutil
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class AudioRecorder(QObject):
    """
    Real audio recorder using sounddevice.
    
    Features:
    - List available audio devices
    - Record from selected device
    - Configurable sample rate and channels
    - Save to WAV files
    - Thread-safe recording
    """
    
    recording_started = Signal()
    recording_stopped = Signal(bytes)  # audio data
    error_occurred = Signal(str)  # error message
    level_changed = Signal(float)  # normalized level for VU meter
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config
        
        # Recording parameters
        self.sample_rate = 16000  # 16kHz for Whisper
        self.channels = 1  # Mono
        self.dtype = 'int16'  # 16-bit audio
        self.debug_audio_dir = Path("data/audio")
        self.debug_audio_dir.mkdir(parents=True, exist_ok=True)
        
        # State
        self.is_recording = False
        self.audio_data = []
        self._last_level = 0.0
        self.device_id = None  # None = default device
        audio_cfg = None
        if self.config:
            try:
                audio_cfg = self.config.get('audio')
            except Exception:
                audio_cfg = None
        if audio_cfg and getattr(audio_cfg, 'device_id', None) is not None:
            self.device_id = audio_cfg.device_id
        else:
            default = self.get_default_device()
            if default:
                self.device_id = default['id']
        
        logger.info(f"AudioRecorder initialized (sample_rate={self.sample_rate}, channels={self.channels})")
    
    @staticmethod
    def list_devices() -> List[Dict]:
        """
        Get list of available audio input devices.
        
        Returns:
            List of device dicts with 'id', 'name', 'channels', 'sample_rate'
        """
        try:
            devices = sd.query_devices()
            input_devices = []
            
            for idx, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'id': idx,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': int(device['default_samplerate']),
                        'is_default': idx == sd.default.device[0]
                    })
            
            logger.info(f"Found {len(input_devices)} input devices")
            return input_devices
            
        except Exception as e:
            logger.error(f"Failed to list devices: {e}")
            return []
    
    @staticmethod
    def get_default_device() -> Optional[Dict]:
        """Get the default input device."""
        devices = AudioRecorder.list_devices()
        for device in devices:
            if device['is_default']:
                return device
        return devices[0] if devices else None
    
    def set_device(self, device_id: Optional[int]):
        """Set the recording device by ID (None for default)."""
        self.device_id = device_id
        if device_id is not None:
            logger.info(f"Audio device set to ID: {device_id}")
        else:
            logger.info("Audio device set to system default")
    
    def set_sample_rate(self, sample_rate: int):
        """Set recording sample rate."""
        self.sample_rate = sample_rate
        logger.info(f"Sample rate set to: {sample_rate} Hz")
    
    def start_recording(self):
        """Start recording audio from microphone."""
        if self.is_recording:
            logger.warning("Already recording")
            return
        
        try:
            self.audio_data = []
            self.is_recording = True
            
            logger.info(f"Starting recording (device={self.device_id}, rate={self.sample_rate}Hz)")
            
            # Start input stream
            self.stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=self.dtype,
                callback=self._audio_callback
            )
            self.stream.start()
            
            self.recording_started.emit()
            logger.info("Recording started successfully")
            
        except Exception as e:
            self.is_recording = False
            error_msg = f"Failed to start recording: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input stream."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Store audio data
        if self.is_recording:
            chunk = indata.copy()
            self.audio_data.append(chunk)
            try:
                rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
                normalized = min(1.0, rms / np.iinfo(np.int16).max * 4.0)
                self._last_level = normalized
                self.level_changed.emit(normalized)
            except Exception:
                pass
    
    def stop_recording(self) -> bytes:
        """
        Stop recording and return audio data.
        
        Returns:
            Audio data as bytes (WAV format)
        """
        if not self.is_recording:
            logger.warning("Not currently recording")
            return b""
        
        try:
            self.is_recording = False
            
            # Stop stream
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()
                del self.stream  # Ensure complete cleanup
            # Concatenate all audio chunks
            if not self.audio_data:
                logger.warning("No audio data captured")
                self.recording_stopped.emit(b"")
                return b""
            
            audio_array = np.concatenate(self.audio_data, axis=0)
            duration = len(audio_array) / self.sample_rate
            
            logger.info(f"Recording stopped: {duration:.2f}s, {len(audio_array)} samples")
            
            # Save to temporary WAV file and read as bytes
            temp_path = Path("temp_recording.wav")
            sf.write(temp_path, audio_array, self.sample_rate)
            
            with open(temp_path, 'rb') as f:
                audio_bytes = f.read()

            self._save_debug_recording(temp_path)
            
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
            
            self.recording_stopped.emit(audio_bytes)
            return audio_bytes
            
        except Exception as e:
            error_msg = f"Failed to stop recording: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return b""

    def _save_debug_recording(self, temp_path: Path):
        """Persist the most recent recording so users can listen for debugging."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            latest_path = self.debug_audio_dir / "latest_recording.wav"
            history_path = self.debug_audio_dir / f"recording_{timestamp}.wav"

            shutil.copy2(temp_path, latest_path)
            shutil.copy2(temp_path, history_path)
            logger.info(f"Saved last recording to {latest_path} (archived as {history_path.name})")
            
            # Clean up old recordings
            self._cleanup_old_recordings()
        except Exception as e:
            logger.debug(f"Failed to save debug recording: {e}")
    
    def _cleanup_old_recordings(self, max_age_days: int = 5, max_size_mb: int = 100):
        """
        Clean up old recording files based on age and total size.
        
        Args:
            max_age_days: Delete recordings older than this many days (default: 5)
            max_size_mb: If folder exceeds this size, delete oldest files (default: 100MB)
        """
        try:
            from datetime import timedelta
            import time
            
            # Get all recording files (exclude latest_recording.wav)
            recording_files = [
                f for f in self.debug_audio_dir.glob("recording_*.wav")
                if f.name != "latest_recording.wav"
            ]
            
            if not recording_files:
                return
            
            current_time = time.time()
            cutoff_time = current_time - (max_age_days * 24 * 60 * 60)
            
            # Delete files older than max_age_days
            deleted_count = 0
            for file_path in recording_files[:]:
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    recording_files.remove(file_path)
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} recordings older than {max_age_days} days")
            
            # Check total folder size
            total_size = sum(f.stat().st_size for f in recording_files) / (1024 * 1024)  # MB
            
            if total_size > max_size_mb:
                # Sort by modification time (oldest first)
                recording_files.sort(key=lambda f: f.stat().st_mtime)
                
                # Delete oldest files until we're under the limit
                while total_size > max_size_mb and recording_files:
                    oldest_file = recording_files.pop(0)
                    file_size = oldest_file.stat().st_size / (1024 * 1024)
                    oldest_file.unlink()
                    total_size -= file_size
                    deleted_count += 1
                
                logger.info(f"Cleaned up {deleted_count} recordings to stay under {max_size_mb}MB limit")
        
        except Exception as e:
            logger.warning(f"Failed to cleanup old recordings: {e}")
    
    def save_recording(self, audio_data: bytes, output_path: Path) -> bool:
        """
        Save audio data to file.
        
        Args:
            audio_data: Audio bytes (WAV format)
            output_path: Path to save WAV file
            
        Returns:
            True if successful
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"Saved recording to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save recording: {e}")
            return False
    
    def get_recording_level(self) -> float:
        """
        Get current recording level (0.0 to 1.0).
        Useful for volume meters during recording.
        
        Returns:
            Volume level normalized to 0.0-1.0
        """
        if not self.is_recording or not self.audio_data:
            return 0.0
        
        return self._last_level
