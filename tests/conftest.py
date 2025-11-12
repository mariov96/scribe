"""
Shared pytest fixtures for test suite.
"""

import os
import sys
import pytest
from pytestqt.qt_compat import qt_api
from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme

# Configure Qt test environment
os.environ['QT_QPA_PLATFORM'] = 'minimal'

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture(scope='session')
def qt_app_args():
    """Arguments for Qt application."""
    return []

@pytest.fixture(scope='session')
def qt_app_cls():
    """Qt application class to use."""
    return QApplication

@pytest.fixture(scope='session')
def qapp(qt_app_args, qt_app_cls):
    """Setup QApplication instance with dark theme."""
    app = qt_api.QtWidgets.QApplication.instance()
    if not app:
        app = qt_app_cls(qt_app_args)
        print("QApplication created")
        try:
            setTheme(Theme.DARK)
            print("Theme set to dark")
        except:
            print("Warning: Could not set theme")
    return app


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "hotkey": {
            "combination": "ctrl+alt",
            "mode": "toggle"
        },
        "audio": {
            "sample_rate": 16000,
            "channels": 1,
            "device_id": None
        },
        "whisper": {
            "model": "tiny",  # Use tiny for fast tests
            "device": "cpu",
            "compute_type": "int8",
            "language": None
        },
        "ai_formatting": {
            "enabled": True,
            "remove_filler_words": True,
            "smart_punctuation": True
        },
        "general": {
            "minimize_to_tray": False,
            "auto_insert_mode": "paste"
        }
    }


@pytest.fixture
def sample_transcription_entry():
    """Sample transcription entry for testing"""
    from datetime import datetime
    return {
        "timestamp": datetime.now(),
        "text": "This is a test transcription",
        "application": "Test App",
        "window_title": "Test Window - Test App",
        "window_handle": 12345,
        "audio_duration": 2.5,
        "word_count": 5,
        "character_count": 28,
        "confidence": 0.95
    }


@pytest.fixture
def mock_plugin():
    """Mock plugin for testing"""
    from scribe.plugins.base import BasePlugin, CommandDefinition
    
    class MockPlugin(BasePlugin):
        name = "mock_plugin"
        version = "1.0.0"
        description = "Mock plugin for testing"
        
        def __init__(self):
            self.initialized = False
            self.commands_called = []
        
        def commands(self):
            return [
                CommandDefinition(
                    patterns=["test command", "test {param}"],
                    handler=self.test_handler,
                    examples=["test command", "test hello"],
                    description="Test command handler"
                )
            ]
        
        def initialize(self, config):
            self.initialized = True
            return True
        
        def shutdown(self):
            self.initialized = False
        
        def test_handler(self, param=None):
            self.commands_called.append({"handler": "test_handler", "param": param})
            return f"Executed with param={param}"
    
    return MockPlugin()