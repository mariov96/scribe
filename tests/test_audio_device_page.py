"""
Comprehensive test suite for AudioDevicePage.

Tests both UI functionality and audio device handling.
"""

import os
os.environ['QT_QPA_PLATFORM'] = 'minimal'

import sys
import asyncio
import pytest
import numpy as np
import sounddevice as sd
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt
from qfluentwidgets import Theme, setTheme

# Mock keyboard module
sys.modules['keyboard'] = MagicMock()

# Simple widget for testing
class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Test")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

# Now import scribe components
from scribe.ui_fluent.setup_wizard.audio_device_page import AudioDevicePage
from scribe.ui_fluent.setup_wizard.base_page import ValidationState

# Tests use fixtures from conftest.py

@pytest.fixture
def audio_page(qtbot, qapp, request):
    """Create AudioDevicePage instance"""
    # Create parent widget first
    parent = QWidget()
    qtbot.addWidget(parent)
    
    # Create AudioDevicePage with parent
    page = AudioDevicePage(parent)
    page.show()
    
    def cleanup():
        """Ensure proper cleanup even if test times out"""
        try:
            if hasattr(page, 'level_timer') and page.level_timer.isActive():
                page.level_timer.stop()
            if page.is_recording:
                page.is_recording = False
            page.cleanup()
            page.hide()
            page.deleteLater()
            parent.deleteLater()
        except:
            pass  # Ignore cleanup errors
    
    request.addfinalizer(cleanup)
    return page

# Mock audio devices
@pytest.fixture
def mock_devices():
    return [
        {
            'index': 0,
            'name': 'Test Mic 1', 
            'max_input_channels': 2, 
            'default_samplerate': 44100,
            'hostapi': 0
        },
        {
            'index': 1,
            'name': 'Test Mic 2', 
            'max_input_channels': 1, 
            'default_samplerate': 48000,
            'hostapi': 0
        },
        {
            'index': 2,
            'name': 'Test Speaker', 
            'max_input_channels': 0, 
            'max_output_channels': 2,
            'hostapi': 0
        }
    ]

# Tests
def test_basic_widget(qtbot, qapp):
    """Test that basic Qt widgets work"""
    widget = TestWidget()
    qtbot.addWidget(widget)
    assert widget.label.text() == "Test"

@pytest.fixture(scope='function')
def qt_test_app():
    """Create a QApplication instance for testing."""
    app = QApplication.instance()
    if not app:
        print("Creating QApplication for test...")
        app = QApplication([])
        from qfluentwidgets import setTheme, Theme
        setTheme(Theme.DARK)
    return app

# Use pytest-qt's fixtures

def test_initial_state(qtbot):
    """Test initial state test."""
    # Create a QApplication using pytest-qt's infrastructure
    print("Test started...")
    
    # Create parent widget and wait for it
    print("Creating parent widget")
    parent = QWidget()
    parent.resize(800, 600)
    qtbot.addWidget(parent)
    
    # Create AudioDevicePage with specific testing mode
    print("Creating AudioDevicePage")
    try:
        with qtbot.waitExposed(parent):
            page = AudioDevicePage(parent)
            qtbot.addWidget(page)
            
        # Run assertions
        print("Running assertions")
        assert page.selected_device is None, "Initial device should be None"
        assert not page.is_recording, "Should not be recording initially"
        assert not page.device_test_passed, "Device test should not be passed initially"
        assert page.get_validation_state() == ValidationState.INVALID, "Initial state should be invalid"
        
        # Clean up
        print("Cleaning up...")
        page.cleanup()
        page.close()
        parent.close()
    except Exception as e:
        print(f"Test error: {e}")
        raise
    finally:
        print("Test complete")

@pytest.mark.timeout(5)  # 5 second timeout
def test_device_population(audio_page, mock_devices, qtbot):
    """Test device population with mock devices"""
    from PySide6.QtCore import QTimer
    
    # Create timeout timer
    timeout_timer = QTimer()
    timeout_timer.setSingleShot(True)
    timeout_timer.setInterval(4000)  # 4 second timeout
    timeout_timer.timeout.connect(lambda: pytest.fail("Test timed out"))
    
    with patch('sounddevice.query_devices', return_value=mock_devices), \
         patch('sounddevice.query_hostapis', return_value=[{'name': 'Mock API', 'devices': [0, 1, 2]}]), \
         patch('sounddevice.check_input_settings') as mock_check:
             
        # Start timeout timer
        timeout_timer.start()
        
        # Setup signal to detect when population is complete
        population_done = False
        def on_populated():
            nonlocal population_done
            population_done = True
        
        # Connect to combobox signal
        audio_page.device_combo.currentIndexChanged.connect(on_populated)
        
        # Populate devices
        audio_page._populate_devices()
        
        # Wait for population with timeout
        with qtbot.waitSignal(audio_page.device_combo.currentIndexChanged, timeout=5000):
            # Should only show input devices
            assert audio_page.device_combo.count() == 2
            assert audio_page.device_combo.itemText(0).startswith('Test Mic 1')
            assert audio_page.device_combo.itemText(1).startswith('Test Mic 2')
        
        # Verify check_input_settings was called with correct parameters
        mock_check.assert_called_with(
            device=0,
            channels=2,
            samplerate=44100,
            dtype='float32'
        )

@pytest.mark.timeout(10)  # 10 second timeout
def test_device_selection(audio_page, mock_devices, qtbot):
    """Test device selection behavior"""
    with patch('sounddevice.query_devices', return_value=mock_devices), \
         patch('sounddevice.query_hostapis', return_value=[{'name': 'Mock API', 'devices': [0, 1, 2]}]), \
         patch('sounddevice.check_input_settings'):
        
        # Populate devices first
        audio_page._populate_devices()
        qtbot.wait(100)  # Small delay for UI update
        
        # Test device selection
        with qtbot.waitSignal(audio_page.device_combo.currentIndexChanged, timeout=1000):
            audio_page.device_combo.setCurrentIndex(0)
        
        # Verify selection state
        assert audio_page.selected_device is not None
        assert audio_page.test_button.isEnabled()
        assert audio_page.get_validation_state() == ValidationState.INVALID
        
        # Test clearing selection
        with qtbot.waitSignal(audio_page.device_combo.currentIndexChanged, timeout=1000):
            audio_page.device_combo.setCurrentIndex(-1)
        
        # Verify cleared state
        assert audio_page.selected_device is None
        assert not audio_page.test_button.isEnabled()

@pytest.mark.asyncio
async def test_recording_success(audio_page, mock_devices):
    """Test successful recording flow"""
    with patch('sounddevice.query_devices', return_value=mock_devices), \
         patch('sounddevice.query_hostapis', return_value=[{'name': 'Mock API', 'devices': [0, 1, 2]}]), \
         patch('sounddevice.check_input_settings'), \
         patch('sounddevice.InputStream') as mock_stream:
        
        # Setup mock audio data
        mock_data = np.random.rand(1000, 1) * 0.5  # Decent audio levels
        mock_instance = MagicMock()
        
        # Setup mock stream context manager
        mock_stream.return_value.__enter__.return_value = mock_instance
        
        # Setup mock callback
        def mock_callback(indata, frames, time, status):
            if audio_page.is_recording:
                audio_page.audio_data.append(mock_data)
        
        mock_instance.read.return_value = (mock_data, None)  # (data, overflowed)
        
        audio_page._populate_devices()
        audio_page.device_combo.setCurrentIndex(0)
        
        # Start test recording
        audio_page._test_recording()
        
        # Start test recording
        audio_page._test_recording()
        await asyncio.sleep(0.1)  # Let async code run
        
        assert audio_page.device_test_passed
        assert audio_page.get_validation_state() == ValidationState.VALID

@pytest.mark.asyncio
async def test_recording_failure_no_audio(audio_page, mock_devices):
    """Test recording with no audio detected"""
    with patch('sounddevice.query_devices', return_value=mock_devices), \
         patch('sounddevice.InputStream') as mock_stream:
        
        # Setup mock audio data - very low levels
        mock_data = np.random.rand(1000, 1) * 0.001
        mock_stream.return_value.__enter__.return_value = MagicMock()
        
        audio_page._populate_devices()
        audio_page.device_combo.setCurrentIndex(0)
        
        def mock_callback(callback):
            callback(mock_data, 1000, 0, None)
            
        mock_stream.side_effect = mock_callback
        
        # Start test recording
        audio_page._test_recording()
        await asyncio.sleep(0.1)
        
        assert not audio_page.device_test_passed
        assert audio_page.get_validation_state() == ValidationState.INVALID
        assert "No audio detected" in audio_page.status_label.text()

@pytest.mark.parametrize("test_data,expected_state,expected_message", [
    ({"rms": 0.001, "peak": 0.99}, ValidationState.INVALID, "Audio levels too high"),
    ({"rms": 0.0001, "peak": 0.001}, ValidationState.INVALID, "Audio levels too low"),
    ({"rms": 0.3, "peak": 0.5}, ValidationState.VALID, "working correctly"),
])
async def test_audio_quality_analysis(audio_page, mock_devices, test_data, expected_state, expected_message):
    """Test audio quality analysis with different scenarios"""
    with patch('sounddevice.query_devices', return_value=mock_devices), \
         patch('sounddevice.InputStream') as mock_stream:
        
        mock_stream.return_value.__enter__.return_value = MagicMock()
        audio_page._populate_devices()
        audio_page.device_combo.setCurrentIndex(0)
        
        # Simulate recording with test data
        test_audio = np.random.rand(1000, 1) * test_data["peak"]
        audio_page.audio_data = [test_audio]
        audio_page.audio_stats = [
            {'rms': test_data["rms"], 
             'peak': test_data["peak"], 
             'amplitude': test_data["rms"]}
        ]
        
        # Trigger analysis
        audio_page._test_recording()
        await asyncio.sleep(0.1)
        
        assert audio_page.get_validation_state() == expected_state
        assert expected_message in audio_page.status_label.text()

def test_recording_error_handling(audio_page, mock_devices):
    """Test handling of recording errors"""
    with patch('sounddevice.query_devices', return_value=mock_devices), \
         patch('sounddevice.InputStream', side_effect=Exception("Test error")):
        
        audio_page._populate_devices()
        audio_page.device_combo.setCurrentIndex(0)
        
        # Start test recording
        audio_page._test_recording()
        
        assert not audio_page.device_test_passed
        assert audio_page.get_validation_state() == ValidationState.ERROR
        assert "Test error" in audio_page.status_label.text()

def test_wsl_environment(audio_page):
    """Test WSL environment detection and handling"""
    with patch.dict('os.environ', {'WSL_DISTRO_NAME': 'Ubuntu'}), \
         patch('subprocess.run') as mock_run:
        
        # Mock successful PulseAudio checks
        mock_run.return_value.stdout = "pulseaudio running"
        
        audio_page._populate_devices()
        
        assert audio_page.device_combo.count() > 0
        assert "WSL" in audio_page.status_label.text()

def test_cleanup(audio_page):
    """Test cleanup of resources"""
    audio_page.is_recording = True
    audio_page.level_timer.start()
    
    audio_page.cleanup()
    
    assert not audio_page.is_recording
    assert not audio_page.level_timer.isActive()

def test_validation_data(audio_page, mock_devices):
    """Test validation and data collection"""
    with patch('sounddevice.query_devices', return_value=mock_devices):
        audio_page._populate_devices()
        audio_page.device_combo.setCurrentIndex(0)
        audio_page.device_test_passed = True
        
        assert audio_page.validate()
        
        data = audio_page.get_data()
        assert 'audio_device' in data
        assert 'audio_device_index' in data
        assert 'sample_rate' in data
        assert data['device_test_passed']

def run_tests_with_timeout():
    """Run tests with timeout protection"""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Tests took too long to complete")
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second global timeout
    
    try:
        pytest.main([__file__, "-v", "--capture=no"])
    except TimeoutError as e:
        print(f"Test suite timed out: {e}")
    finally:
        signal.alarm(0)  # Disable alarm

if __name__ == '__main__':
    run_tests_with_timeout()