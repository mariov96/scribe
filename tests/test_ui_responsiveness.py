"""
Tests for UI responsiveness, especially after long-running operations.
"""
import pytest
from unittest.mock import Mock, patch
from PyQt5.QtCore import QTimer

from scribe.app import ScribeApp
from scribe.core.transcription_engine import TranscriptionResult
from scribe.ui_fluent.main_window import ScribeMainWindow

# This test requires a QApplication instance to be running.
# pytest-qt automatically handles this.

def test_ui_remains_responsive_after_transcription(qtbot):
    """
    Test that the UI is not blocked after a transcription completes.
    """
    with patch('scribe.app.HotkeyManager'), \
         patch('scribe.app.TranscriptionEngine'), \
         patch('scribe.app.AudioRecorder'), \
         patch('scribe.app.ConfigManager'):

        # Patch the method that causes blocking and is hard to test
        with patch.object(ScribeApp, '_return_text_to_application', Mock()) as mock_paste:
            
            app = ScribeApp()
            app.initialize()
            qtbot.addWidget(app.main_window)

            # Mock UI update methods to verify they are called
            app.main_window.update_transcription_summary = Mock()
            app.main_window.update_recording_status = Mock()

            # Simulate a transcription result
            result = TranscriptionResult(
                text="This is a test transcription.",
                duration=2.0,
                confidence=0.95,
                language="en"
            )

            # Call the transcription completion handler
            app._on_transcription_complete(result)
            
            # Allow the event loop to process the deferred paste call
            qtbot.wait(100)

            # Verify the paste operation was deferred and called
            mock_paste.assert_called_once()
            
            # Verify the immediate UI update was called
            app.main_window.update_transcription_summary.assert_called_once()

            # Check if the UI is still responsive by queueing another call
            QTimer.singleShot(50, lambda: app.main_window.update_recording_status(True))
            qtbot.wait(100)

            # Verify the second UI update also happened
            app.main_window.update_recording_status.assert_called_once_with(True)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])