"""
Tests to verify that the audio recorder captures audio data correctly.
"""
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import time

from scribe.core.audio_recorder import AudioRecorder

@pytest.fixture
def recorder():
    """Fixture for a clean AudioRecorder instance."""
    with patch('scribe.core.audio_recorder.sd.InputStream'), \
         patch('scribe.core.audio_recorder.sd.query_devices', return_value=[
             {'name': 'default', 'max_input_channels': 1, 'default_samplerate': 44100, 'id': 0, 'is_default': True}
         ]):
        recorder = AudioRecorder(config=None)
        yield recorder
        # Cleanup if necessary
        if recorder.is_recording:
            recorder.stop_recording()
        if hasattr(recorder, '_level_timer'):
            recorder._level_timer.stop()

def test_start_and_stop_recording_produces_data(recorder):
    """Test that starting and stopping recording produces a non-empty numpy array."""
    
    # Mock the stream to simulate receiving audio data
    mock_stream = MagicMock()
    
    def mock_callback(indata, frames, time, status):
        # Simulate receiving some audio data
        pass

    with patch('scribe.core.audio_recorder.sd.InputStream', return_value=mock_stream):
        recorder.start_recording()
        
        # Simulate audio data being added in the callback
        test_chunk = np.random.randint(-1000, 1000, size=(1024, 1), dtype=np.int16)
        recorder.audio_data.append(test_chunk)
        
        time.sleep(0.1) # Simulate a short recording
        
        audio_array = recorder.stop_recording()

    assert isinstance(audio_array, np.ndarray), "Should return a numpy array"
    assert audio_array.size > 0, "Audio array should not be empty"
    assert audio_array.shape == (1024, 1), "Audio array shape is incorrect"

def test_stop_recording_with_no_data(recorder):
    """Test that stopping recording with no data returns an empty array."""
    
    # Start and immediately stop recording without simulating any data
    with patch('scribe.core.audio_recorder.sd.InputStream'):
        recorder.start_recording()
        # No data is added
        audio_array = recorder.stop_recording()

    assert isinstance(audio_array, np.ndarray), "Should return a numpy array"
    assert audio_array.size == 0, "Audio array should be empty when no data is captured"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])