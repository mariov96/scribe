"""
Core functionality test suite for Scribe.
Tests critical features and known issues.
"""

import sys
import unittest
from pathlib import Path
import tempfile
import numpy as np
from unittest.mock import MagicMock, patch
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scribe.core.transcription_engine import TranscriptionEngine
from src.scribe.core.audio_recorder import AudioRecorder
from src.scribe.core.hotkey_manager import HotkeyManager
from src.scribe.ui_fluent.components.device_selector import DeviceSelector

class TestCoreFeatures(unittest.TestCase):
    """Test core functionality and known issues."""
    
    @unittest.skip("Skipping transcription tests temporarily")
    def setUp(self):
        """Set up test environment."""
        self.config = {'model_options': {'device': 'cpu'}}
        
    def test_transcription_engine_init(self):
        """Test transcription engine initialization."""
        config = {'model_options': {'device': 'cpu'}}
        engine = TranscriptionEngine(config)
        success = engine.initialize()
        self.assertTrue(success)
        # Model is initialized
        self.assertIsNotNone(engine.model)
        self.assertEqual(engine.model.compute_type, "int8")
    
    def test_audio_recording_cleanup(self):
        """Test audio recording cleanup on stop."""
        recorder = AudioRecorder()
        recorder.start_recording()
        
        # Record for a moment
        import time
        time.sleep(0.1)
        
        # Stop and check cleanup
        audio_data = recorder.stop_recording()
        self.assertFalse(recorder.is_recording)
        # Check if stream is deleted
        self.assertFalse(hasattr(recorder, 'stream'))

class TestWSLIntegration(unittest.TestCase):
    """Test WSL-specific functionality."""
    
    @patch('Xlib.display.Display')
    def test_x11_hotkey_setup(self, mock_display):
        """Test X11 hotkey initialization."""
        mock_display.return_value = MagicMock()
        
        config = {'recording_options': {'activation_key': 'ctrl+meta'}}
        manager = HotkeyManager(config)
        manager.start()
        
        # Verify X11 setup
        self.assertTrue(manager.is_listening)
    
    def test_pulseaudio_detection(self):
        """Test PulseAudio device detection in WSL."""
        recorder = AudioRecorder()
        devices = recorder.list_devices()
        
        # Should find at least one device
        self.assertTrue(len(devices) > 0, "No audio devices found")
        
        # Get first device
        first_device = devices[0]
        
        # Required fields in every device
        required_fields = {'id', 'name', 'channels', 'sample_rate', 'is_default'}
        
        # Check all required fields exist
        for field in required_fields:
            self.assertIn(field, first_device, f"Missing required field: {field}")
        
        # Validate field types
        self.assertIsInstance(first_device['id'], int, "Device ID should be integer")
        self.assertIsInstance(first_device['name'], str, "Device name should be string")
        self.assertIsInstance(first_device['channels'], int, "Channels should be integer")
        self.assertIsInstance(first_device['sample_rate'], int, "Sample rate should be integer")
        self.assertIsInstance(first_device['is_default'], bool, "is_default should be boolean")

class TestUIComponents(unittest.TestCase):
    """Test UI component issues."""
    
    def setUp(self):
        from PySide6.QtWidgets import QApplication
        self.app = QApplication.instance() or QApplication(sys.argv)
    
    def test_device_selector_icons(self):
        """Test device selector combo box icons."""
        recorder = AudioRecorder()
        devices = recorder.list_devices()
        
        selector = DeviceSelector()
        
        # Add devices properly
        for device in devices:
                selector.add_device(device['name'], device['id'])        # Verify icon handling
        self.assertGreater(selector.count(), 0)
        
        # Get first item
        first_item = selector.itemData(0)
        self.assertIsNotNone(first_item)
    
    def test_system_tray(self):
        """Test system tray integration with fallback."""
        from PySide6.QtWidgets import QSystemTrayIcon
        
        # Test the fallback mode
        tray = QSystemTrayIcon()
        # Just verify it can be created and shown without errors
        tray.show()
        self.assertIsNotNone(tray)
        tray.hide()
        
        # Even if DBus isn't available, should still work
        tray.show()
        self.assertTrue(tray.isVisible())

def run_tests():
    """Run core feature tests."""
    logging.basicConfig(level=logging.INFO)
    print("\n=== Running Core Feature Tests ===\n")
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests()