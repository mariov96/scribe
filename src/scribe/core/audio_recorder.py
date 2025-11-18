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
from PyQt5.QtCore import QObject, pyqtSignal as Signal, QTimer

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
        self._is_monitoring = False
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
    def can_open(device_id: Optional[int], sample_rate: int = 16000, channels: int = 1) -> bool:
        """Lightweight probe to verify a device can open at the given sample rate.

        Returns True when an InputStream can be created and started; closes immediately.
        Never raises; logs and returns False on failure.
        """
        try:
            stream = sd.InputStream(
                device=device_id,
                channels=channels,
                samplerate=sample_rate,
                dtype='int16',
                blocksize=0,
                latency=None,
                callback=None,
            )
            # Some drivers require start/stop to fully validate
            stream.start()
            stream.stop()
            stream.close()
            return True
        except Exception as e:
            logger.debug(f"Device open probe failed (id={device_id}, rate={sample_rate}): {e}")
            return False

    @staticmethod
    def list_valid_input_devices(sample_rate: int = 16000, channels: int = 1) -> List[Dict]:
        """Return only input devices that successfully open at the given sample rate."""
        devices = AudioRecorder.list_devices()
        valid: List[Dict] = []
        for d in devices:
            if d.get('channels', 0) > 0 and AudioRecorder.can_open(d['id'], sample_rate, channels):
                valid.append(d)
        logger.info(f"Filtered valid input devices: {len(valid)} / {len(devices)}")
        return valid
    
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
            # Validate device before starting
            if self.device_id is not None:
                try:
                    device_info = sd.query_devices(self.device_id)
                    if device_info['max_input_channels'] < 1:
                        raise ValueError(f"Device {self.device_id} has no input channels")
                    logger.info(f"Validated device: {device_info['name']}")
                except Exception as e:
                    logger.error(f"Invalid device {self.device_id}: {e}. Falling back to default.")
                    self.device_id = None
            
            self.audio_data = []
            self.is_recording = True

            logger.info(f"Starting recording (device={self.device_id}, rate={self.sample_rate}Hz)")

            # Start input stream with error handling
            try:
                # Create callback wrapper to avoid Qt issues
                def audio_callback_wrapper(indata, frames, time_info, status):
                    """Wrapper to call the instance method safely."""
                    try:
                        self._audio_callback(indata, frames, time_info, status)
                    except Exception as e:
                        # Silently catch errors to prevent stream crash
                        pass

                self.stream = sd.InputStream(
                    device=self.device_id,
                    channels=self.channels,
                    samplerate=self.sample_rate,
                    dtype=self.dtype,
                    callback=audio_callback_wrapper,
                    blocksize=0,  # Use default block size for stability
                    latency=None  # Let PortAudio decide latency
                )
                self.stream.start()
            except sd.PortAudioError as e:
                raise RuntimeError(f"PortAudio error: {e}. Device may be in use or unavailable.") from e

            # Start timer to emit level changes from main thread (not audio thread)
            self._level_timer = QTimer(self)
            self._level_timer.timeout.connect(self._emit_level)
            self._level_timer.start(50)  # Update 20 times per second

            self.recording_started.emit()
            logger.info("Recording started successfully")
            
        except Exception as e:
            self.is_recording = False
            error_msg = f"Failed to start recording: {e}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
    
    def _emit_level(self):
        """Emit level change from main thread (called by timer)."""
        if (self.is_recording or self._is_monitoring) and hasattr(self, '_last_level'):
            self.level_changed.emit(self._last_level)
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input stream - runs in audio thread!"""
        try:
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
                    # DON'T emit Qt signals from audio thread - causes segfault!
                    # Signal will be emitted from main thread via timer
                except Exception as e:
                    # Don't log every callback error, just first one
                    if not hasattr(self, '_callback_error_logged'):
                        logger.error(f"Audio callback error: {e}", exc_info=True)
                        self._callback_error_logged = True
        except Exception as e:
            # Catch any unhandled callback errors to prevent crashes
            logger.error(f"Critical audio callback error: {e}", exc_info=True)
            self.is_recording = False
    
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
            
            # Stop level timer if not used by monitoring
            if hasattr(self, '_level_timer'):
                self._level_timer.stop()
                self._level_timer.deleteLater()
                del self._level_timer
            
            # Stop stream with error handling
            if hasattr(self, 'stream'):
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception as e:
                    logger.error(f"Error stopping audio stream: {e}", exc_info=True)
                finally:
                    if hasattr(self, 'stream'):
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

    # --- Lightweight input level monitoring (no audio accumulation) ---
    def start_level_monitor(self, device_id: Optional[int] = None, sample_rate: int = 16000, channels: int = 1):
        """Start a lightweight input stream that only computes and emits levels.

        Opens an InputStream and updates `_last_level` from its callback, without
        accumulating audio buffers. Emits `level_changed` via a QTimer.
        """
        if self._is_monitoring:
            logger.warning("Already monitoring levels")
            return
        if self.is_recording:
            raise RuntimeError("Cannot start level monitor while recording")

        try:
            self._is_monitoring = True
            # Use provided device if given, otherwise current, otherwise default
            monitor_device = device_id if device_id is not None else self.device_id
            # Validate/openability early
            if monitor_device is not None and not AudioRecorder.can_open(monitor_device, sample_rate, channels):
                raise RuntimeError("Selected device cannot be opened for monitoring")

            def monitor_callback(indata, frames, time_info, status):
                try:
                    if status:
                        logger.debug(f"Monitor status: {status}")
                    chunk = indata
                    rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
                    normalized = min(1.0, rms / np.iinfo(np.int16).max * 4.0)
                    self._last_level = normalized
                except Exception:
                    pass

            self._monitor_stream = sd.InputStream(
                device=monitor_device,
                channels=channels,
                samplerate=sample_rate,
                dtype='int16',
                callback=monitor_callback,
                blocksize=0,
                latency=None,
            )
            self._monitor_stream.start()

            # Timer to emit level updates
            self._level_timer = QTimer(self)
            self._level_timer.timeout.connect(self._emit_level)
            self._level_timer.start(50)
            logger.info("Level monitoring started")
        except Exception as e:
            self._is_monitoring = False
            if hasattr(self, '_monitor_stream'):
                try:
                    self._monitor_stream.stop()
                    self._monitor_stream.close()
                except Exception:
                    pass
                finally:
                    del self._monitor_stream
            raise

    def stop_level_monitor(self):
        """Stop the level monitoring stream if active."""
        if not self._is_monitoring:
            return
        try:
            if hasattr(self, '_level_timer'):
                self._level_timer.stop()
                self._level_timer.deleteLater()
                del self._level_timer
            if hasattr(self, '_monitor_stream'):
                try:
                    self._monitor_stream.stop()
                    self._monitor_stream.close()
                except Exception as e:
                    logger.debug(f"Error stopping monitor stream: {e}")
                finally:
                    del self._monitor_stream
            logger.info("Level monitoring stopped")
        finally:
            self._is_monitoring = False
