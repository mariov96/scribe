"""
Integration test for audio recording - tests the actual recording flow.
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import QTimer, QCoreApplication
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp(qapp):
    """Ensure Qt application is running."""
    return qapp


@pytest.mark.integration
def test_recording_starts_without_crash(qapp):
    """Test that recording can start without segfault (thread safety)."""
    from scribe.core.audio_recorder import AudioRecorder
    
    # Create recorder
    recorder = AudioRecorder(config=None)
    
    # Track if signals were emitted
    started_called = []
    level_called = []
    error_called = []
    
    recorder.recording_started.connect(lambda: started_called.append(True))
    recorder.level_changed.connect(lambda level: level_called.append(level))
    recorder.error_occurred.connect(lambda msg: error_called.append(msg))
    
    try:
        # Start recording (this will use real audio device)
        recorder.start_recording()
        
        # Process events to let Qt signals propagate
        qapp.processEvents()
        
        # Give it a moment to actually start
        time.sleep(0.2)
        qapp.processEvents()
        
        # Check that recording started
        assert recorder.is_recording, "Recording should be active"
        assert started_called, "recording_started signal should have been emitted"
        assert not error_called, f"Should not have errors: {error_called}"
        
        # Let it record for a bit to test the audio callback
        time.sleep(0.5)
        qapp.processEvents()
        
        # Should have received some level updates (via timer, not callback!)
        # If this works without crash, the thread safety fix is working
        assert len(level_called) > 0, "Should have received level updates from timer"
        
        # Stop recording
        audio_data = recorder.stop_recording()
        qapp.processEvents()
        
        # Should have some audio data
        assert len(audio_data) > 0, "Should have captured some audio"
        assert not recorder.is_recording, "Recording should be stopped"
        
    except Exception as e:
        # If we get here with a segfault, the test will fail
        pytest.fail(f"Recording crashed: {e}")
    finally:
        # Cleanup
        if recorder.is_recording:
            recorder.stop_recording()


@pytest.mark.integration  
@patch('scribe.core.audio_recorder.sd.InputStream')
def test_recording_with_mock_stream(mock_stream_class, qapp):
    """Test recording flow with mocked audio stream."""
    from scribe.core.audio_recorder import AudioRecorder
    import numpy as np
    
    # Setup mock stream
    mock_stream = MagicMock()
    mock_stream_class.return_value = mock_stream
    
    # Create recorder
    recorder = AudioRecorder(config=None)
    
    # Track signals
    signals_received = {
        'started': False,
        'levels': [],
        'stopped': False,
        'errors': []
    }
    
    recorder.recording_started.connect(lambda: signals_received.__setitem__('started', True))
    recorder.level_changed.connect(lambda level: signals_received['levels'].append(level))
    recorder.recording_stopped.connect(lambda data: signals_received.__setitem__('stopped', True))
    recorder.error_occurred.connect(lambda msg: signals_received['errors'].append(msg))
    
    # Start recording
    recorder.start_recording()
    qapp.processEvents()
    
    assert recorder.is_recording
    assert signals_received['started']
    assert mock_stream.start.called
    
    # Simulate audio callback being called (from audio thread)
    # This should NOT emit signals directly
    fake_audio = np.random.randint(-1000, 1000, (1600, 1), dtype=np.int16)
    recorder._audio_callback(fake_audio, 1600, None, None)
    
    # Process events to let timer emit the level signal
    time.sleep(0.1)  # Wait for timer (50ms interval)
    qapp.processEvents()
    
    # Should have level updates from timer, not from callback
    assert len(signals_received['levels']) > 0, "Timer should emit level signals"
    
    # Stop recording
    recorder.stop_recording()
    qapp.processEvents()
    
    assert not recorder.is_recording
    assert mock_stream.stop.called
    assert mock_stream.close.called


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
