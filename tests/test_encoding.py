"""
Tests for encoding issues, particularly with Unicode characters.
"""
import pytest
from unittest.mock import patch, Mock
from scribe.app import ScribeApp
from scribe.core.transcription_engine import TranscriptionResult

def test_unicode_transcription_does_not_raise_error(capsys):
    """
    Test that transcriptions with Unicode characters are handled gracefully.
    """
    with patch('scribe.app.ScribeMainWindow'), \
         patch('scribe.app.HotkeyManager'), \
         patch('scribe.app.TranscriptionEngine'), \
         patch('scribe.app.AudioRecorder'), \
         patch('scribe.app.ConfigManager'):

        app = ScribeApp()
        app.initialize()

        # Simulate a transcription result with a Unicode character
        result = TranscriptionResult(
            text="你好世界",  # "Hello world" in Chinese
            duration=1.0,
            confidence=0.99,
            language="zh"
        )

        # This should not raise a UnicodeEncodeError
        app._on_transcription_complete(result)

        # Check that the output was printed correctly to stdout
        captured = capsys.readouterr()
        assert "你好世界" in captured.out

if __name__ == '__main__':
    pytest.main([__file__, '-v'])