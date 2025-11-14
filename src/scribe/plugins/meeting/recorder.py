"""
Meeting audio recorder
"""

import logging
import time
import wave
import numpy as np
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
import sounddevice as sd

logger = logging.getLogger(__name__)


class MeetingRecorder(QObject):
    """Records audio for meetings"""
    
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    
    def __init__(self, sample_rate=16000, channels=1):
        super().__init__()
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_data = []
        self.start_time = None
    
    def start_recording(self, output_file: str):
        """Start recording audio"""
        if self.is_recording:
            logger.warning("Already recording")
            return
        
        self.audio_data = []
        self.output_file = output_file
        self.start_time = time.time()
        self.is_recording = True
        
        # Start recording in a separate thread
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._audio_callback,
            dtype=np.float32
        )
        self.stream.start()
        
        self.recording_started.emit()
        logger.info(f"Started recording to: {output_file}")
    
    def stop_recording(self) -> float:
        """Stop recording and save audio file. Returns duration in seconds."""
        if not self.is_recording:
            logger.warning("Not recording")
            return 0.0
        
        self.is_recording = False
        
        # Stop stream
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        # Calculate duration
        duration = time.time() - self.start_time if self.start_time else 0.0
        
        # Concatenate all audio chunks
        if self.audio_data:
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            # Save to WAV file
            self._save_wav(audio_array, self.output_file)
            logger.info(f"Saved recording: {self.output_file} ({duration:.1f}s)")
        else:
            logger.warning("No audio data recorded")
        
        self.recording_stopped.emit()
        
        return duration
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        if self.is_recording:
            # Copy audio data
            self.audio_data.append(indata.copy())
    
    def _save_wav(self, audio_data: np.ndarray, filename: str):
        """Save audio data to WAV file"""
        # Ensure parent directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Convert float32 to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Save as WAV
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())
