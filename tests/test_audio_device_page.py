"""
Simplified and robust test suite for AudioDevicePage.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys

# Add src to path to allow for absolute imports
sys.path.insert(0, "src")

from scribe.ui_fluent.setup_wizard.audio_device_page import AudioDevicePage
from scribe.ui_fluent.setup_wizard.base_page import ValidationState

@pytest.fixture
def audio_page(qtbot, qapp):
    """Create a fixture for the AudioDevicePage."""
    page = AudioDevicePage()
    qtbot.addWidget(page)
    return page

@pytest.fixture
def mock_devices():
    """Provides a list of mock audio devices."""
    return [
        {'name': 'Test Mic 1', 'max_input_channels': 1, 'index': 0},
        {'name': 'Test Mic 2', 'max_input_channels': 1, 'index': 1},
        {'name': 'Speakers', 'max_input_channels': 0, 'index': 2},
    ]

def test_initial_state(audio_page):
    """Test the initial state of the AudioDevicePage."""
    assert audio_page.selected_device is None
    assert not audio_page.is_recording
    assert not audio_page.device_test_passed
    assert audio_page.get_validation_state() == ValidationState.INVALID

@patch('sounddevice.query_devices')
def test_device_population(mock_query_devices, audio_page, mock_devices):
    """Test that the device combo box is populated correctly."""
    mock_query_devices.return_value = mock_devices
    
    audio_page._populate_devices()
    
    # Should only show input devices
    assert audio_page.device_combo.count() == 2
    assert "Test Mic 1" in audio_page.device_combo.itemText(0)
    assert "Test Mic 2" in audio_page.device_combo.itemText(1)

def test_device_selection(audio_page, qtbot):
    """Test the behavior of selecting a device."""
    # Manually add items to the combo box for this test
    audio_page.device_combo.addItem("Test Mic 1", userData={'index': 0})
    audio_page.device_combo.addItem("Test Mic 2", userData={'index': 1})

    # Select the first device
    with qtbot.waitSignal(audio_page.device_combo.currentIndexChanged):
        audio_page.device_combo.setCurrentIndex(0)
    
    assert audio_page.selected_device is not None
    assert audio_page.test_button.isEnabled()
    assert audio_page.get_validation_state() == ValidationState.INVALID

@patch('sounddevice.InputStream')
def test_recording_flow(mock_input_stream, audio_page, qtbot):
    """Test the recording and validation flow."""
    # Manually add a device and select it
    audio_page.device_combo.addItem("Test Mic 1", userData={'index': 0})
    audio_page.device_combo.setCurrentIndex(0)

    # Mock the audio stream to provide some data
    mock_stream = MagicMock()
    mock_stream.read.return_value = (MagicMock(), False) # (data, overflowed)
    mock_input_stream.return_value.__enter__.return_value = mock_stream

    # Simulate a successful recording test
    with patch.object(audio_page, '_analyze_audio_quality', return_value=(ValidationState.VALID, "Looks good!")):
        audio_page._test_recording()
        qtbot.wait(3100) # Wait for the recording to finish

    assert audio_page.device_test_passed
    assert audio_page.get_validation_state() == ValidationState.VALID
    assert "Looks good!" in audio_page.status_label.text()

def test_audio_quality_analysis(audio_page):
    """Test the audio quality analysis logic."""
    # Test case 1: Audio levels too high (clipping)
    state, message = audio_page._analyze_audio_quality(rms=0.8, peak=0.99)
    assert state == ValidationState.INVALID
    assert "too high" in message

    # Test case 2: Audio levels too low
    state, message = audio_page._analyze_audio_quality(rms=0.01, peak=0.1)
    assert state == ValidationState.INVALID
    assert "too low" in message

    # Test case 3: Good audio levels
    state, message = audio_page._analyze_audio_quality(rms=0.3, peak=0.6)
    assert state == ValidationState.VALID
    assert "working correctly" in message