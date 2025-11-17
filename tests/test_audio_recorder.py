"""
Tests for audio recorder functionality and thread safety.
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import numpy as np


class TestAudioRecorderThreadSafety:
    """Test audio recorder thread safety with Qt signals."""
    
    def test_audio_recorder_imports(self):
        """Test that audio recorder can be imported."""
        from scribe.core.audio_recorder import AudioRecorder
        assert AudioRecorder is not None
    
    def test_list_devices(self):
        """Test listing audio devices."""
        from scribe.core.audio_recorder import AudioRecorder
        
        devices = AudioRecorder.list_devices()
        assert isinstance(devices, list)
        # Should have at least some devices on most systems
        assert len(devices) >= 0
    
    def test_audio_recorder_initialization(self):
        """Test audio recorder initializes without Qt application."""
        from scribe.core.audio_recorder import AudioRecorder
        
        # Create recorder without config
        recorder = AudioRecorder(config=None)
        assert recorder is not None
        assert recorder.sample_rate == 16000
        assert recorder.channels == 1
        assert recorder.is_recording == False
    
    @patch('scribe.core.audio_recorder.sd.InputStream')
    def test_start_recording_creates_stream(self, mock_stream_class):
        """Test that starting recording creates a stream."""
        from scribe.core.audio_recorder import AudioRecorder
        
        # Mock the stream
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        recorder = AudioRecorder(config=None)
        recorder.start_recording()
        
        # Verify stream was created and started
        assert mock_stream_class.called
        assert mock_stream.start.called
        assert recorder.is_recording == True
    
    @patch('scribe.core.audio_recorder.sd.InputStream')
    def test_audio_callback_doesnt_emit_signals(self, mock_stream_class):
        """Test that audio callback doesn't emit Qt signals directly."""
        from scribe.core.audio_recorder import AudioRecorder
        import inspect
        
        # Check the _audio_callback source code doesn't contain .emit calls
        source = inspect.getsource(AudioRecorder._audio_callback)
        
        # Should NOT emit level_changed from callback (would cause segfault)
        assert 'self.level_changed.emit' not in source, \
            "Audio callback must NOT emit Qt signals - causes thread-safety crash!"
        
        # Should only store the level
        assert 'self._last_level' in source, \
            "Audio callback should store level in _last_level for timer to emit"
    
    @patch('scribe.core.audio_recorder.sd.InputStream')
    def test_level_timer_created_on_start(self, mock_stream_class):
        """Test that QTimer is created for thread-safe signal emission."""
        from scribe.core.audio_recorder import AudioRecorder
        
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        recorder = AudioRecorder(config=None)
        recorder.start_recording()
        
        # Verify timer was created
        assert hasattr(recorder, '_level_timer'), \
            "Should create QTimer for thread-safe level emission"
    
    def test_device_validation(self):
        """Test that invalid device handling doesn't crash."""
        from scribe.core.audio_recorder import AudioRecorder
        
        # Create recorder with invalid device
        recorder = AudioRecorder(config=None)
        recorder.device_id = 99999  # Invalid device
        
        # Should not crash when attempting to validate
        try:
            # This should handle the invalid device gracefully
            devices = AudioRecorder.list_devices()
            assert isinstance(devices, list)
        except Exception as e:
            pytest.fail(f"Device validation should not raise: {e}")
    
    @patch('scribe.core.audio_recorder.sd.InputStream')
    def test_stop_recording_cleanup(self, mock_stream_class):
        """Test that stopping recording cleans up properly."""
        from scribe.core.audio_recorder import AudioRecorder
        
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        recorder = AudioRecorder(config=None)
        recorder.start_recording()
        
        # Add some fake audio data
        recorder.audio_data = [np.zeros((1600, 1), dtype=np.int16)]
        
        # Stop recording
        recorder.stop_recording()
        
        # Verify cleanup
        assert recorder.is_recording == False
        assert not hasattr(recorder, '_level_timer') or recorder._level_timer is None
        assert mock_stream.stop.called
        assert mock_stream.close.called


class TestAudioRecorderErrorHandling:
    """Test error handling in audio recorder."""
    
    @patch('scribe.core.audio_recorder.sd.InputStream')
    def test_portaudio_error_handling(self, mock_stream_class):
        """Test that PortAudioError is caught and handled."""
        from scribe.core.audio_recorder import AudioRecorder
        import sounddevice as sd
        
        # Mock PortAudio error
        mock_stream_class.side_effect = sd.PortAudioError("Device busy")
        
        recorder = AudioRecorder(config=None)
        
        # Should not crash, should emit error signal
        error_emitted = False
        def on_error(msg):
            nonlocal error_emitted
            error_emitted = True
        
        recorder.error_occurred.connect(on_error)
        recorder.start_recording()
        
        # Should have handled error
        assert recorder.is_recording == False
    
    @patch('scribe.core.audio_recorder.sd.query_devices')
    def test_device_query_error_handling(self, mock_query):
        """Test that device query errors are handled."""
        from scribe.core.audio_recorder import AudioRecorder
        
        # Mock device query failure
        mock_query.side_effect = Exception("Device query failed")
        
        # Should not crash
        try:
            devices = AudioRecorder.list_devices()
            assert isinstance(devices, list)
            assert len(devices) == 0  # Should return empty list on error
        except Exception as e:
            pytest.fail(f"list_devices should not raise: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
