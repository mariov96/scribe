"""
Audio Device Page - Audio device selection and testing.

Allows user to select their microphone and test recording.
"""

import os
import subprocess
from typing import Optional, List
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from qfluentwidgets import (
    CardWidget, BodyLabel, StrongBodyLabel,
    ComboBox, PushButton, ProgressBar, InfoBar, InfoBarPosition
)
import sounddevice as sd
import numpy as np

from .base_page import BasePage, ValidationState, QABCMeta


class AudioDevicePage(BasePage):
    """
    Audio device selection and testing page.
    
    Allows user to:
    - Select from available input devices
    - Test recording with visual feedback
    - Verify audio levels are working
    """

    def __init__(self, parent=None):
        """Initialize the audio device page."""
        super().__init__(parent)  # Initialize QWidget through the parent classes
        
        # Initialize instance variables before setting up UI
        self.selected_device = None
        self.is_recording = False
        self.device_test_passed = False
        self.audio_data = []
        self.test_button = None  # Initialize here before setup_ui
        self.device_combo = None
        self.status_label = None
        self.level_bar = None
        self.level_timer = None
        
        # Now set up the UI which will create all widgets
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the audio device page UI."""
        super().setup_ui()
        
        # Main content card - use QWidget initialization pattern
        main_card = CardWidget()
        main_card.setParent(self)  # Set parent after initialization
        card_layout = QVBoxLayout()
        main_card.setLayout(card_layout)  # Set layout after initialization
        card_layout.setContentsMargins(60, 50, 60, 50)
        card_layout.setSpacing(24)
        
        # Instructions
        instructions = BodyLabel()
        instructions.setParent(main_card)  # Set parent
        instructions.setText(
            "Select your microphone from the list below. "
            "We recommend testing it to ensure everything works correctly."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 14px; line-height: 1.6;")
        card_layout.addWidget(instructions)
        
        card_layout.addSpacing(8)
        
        # Device selection section
        device_section = StrongBodyLabel()
        device_section.setParent(main_card)
        device_section.setText("Audio Input Device")
        device_section.setStyleSheet("font-size: 15px;")
        card_layout.addWidget(device_section)
        
        # Device combo box
        self.device_combo = ComboBox()
        self.device_combo.setParent(main_card)
        self.device_combo.setPlaceholderText("Select a microphone...")
        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        card_layout.addWidget(self.device_combo)
        
        # Status label
        self.status_label = BodyLabel()
        self.status_label.setParent(main_card)
        self.status_label.setText("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        card_layout.addWidget(self.status_label)
        
        # Testing section
        card_layout.addSpacing(16)
        test_section = StrongBodyLabel()
        test_section.setParent(main_card)
        test_section.setText("Test Your Microphone")
        test_section.setStyleSheet("font-size: 15px;")
        card_layout.addWidget(test_section)
        
        test_instructions = BodyLabel()
        test_instructions.setParent(main_card)
        test_instructions.setText(
            "Click the button below and speak into your microphone. "
            "You should see the audio level indicator respond to your voice."
        )
        test_instructions.setWordWrap(True)
        test_instructions.setStyleSheet("font-size: 14px; line-height: 1.6;")
        card_layout.addWidget(test_instructions)
        
        card_layout.addSpacing(8)
        
        # Test button
        self.test_button = PushButton()
        self.test_button.setParent(main_card)
        self.test_button.setText("🎤 Test Recording (3 seconds)")
        self.test_button.clicked.connect(self._test_recording)
        self.test_button.setEnabled(False)
        card_layout.addWidget(self.test_button)
        
        # Audio level visualization
        level_label = BodyLabel()
        level_label.setParent(main_card)
        level_label.setText("Audio Level:")
        card_layout.addWidget(level_label)
        
        self.level_bar = ProgressBar()
        self.level_bar.setParent(main_card)
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        card_layout.addWidget(self.level_bar)
        
        # Add main card to page layout
        self.layout.addWidget(main_card)
        self.layout.addStretch()
        
        # Timer for level updates during recording
        self.level_timer = QTimer()
        self.level_timer.setParent(self)
        self.level_timer.timeout.connect(self._update_level)
        
        # Initial validation state
        self.set_validation_state(ValidationState.INVALID, "Please select an audio device")
        
        # Now populate devices
        self._populate_devices()
    
    def _populate_devices(self):
        """Populate the device combo box with available input devices."""
        try:
            self.set_validation_state(ValidationState.PENDING, "Scanning for audio devices...")
            self.status_label.setText("🔍 Scanning for audio devices...")
            
            # Check for WSL environment first
            in_wsl = 'WSL_DISTRO_NAME' in os.environ
            
            if in_wsl:
                print("\n=== WSL Audio Setup ===")
                self._setup_wsl_audio()
            
            # Try to reinitialize sounddevice with a timeout
            try:
                def reinit():
                    sd._terminate()
                    sd._initialize()
                    
                import threading
                init_thread = threading.Thread(target=reinit, daemon=True)
                init_thread.start()
                init_thread.join(timeout=5)  # 5 second timeout
                
                if init_thread.is_alive():
                    print("Sounddevice init timed out - continuing anyway")
                
            except Exception as e:
                print(f"Sounddevice reinit error (non-fatal): {e}")
            
            # Get hostapis and try each one
            found_valid_api = False
            print("\n=== Audio System Info ===")
            try:
                hostapis = sd.query_hostapis()
                print(f"Default Host API: {sd.default.hostapi}")
                
                for i, api in enumerate(hostapis):
                    print(f"Host API {i}: {api['name']}")
                    # Test if this API works
                    try:
                        sd.check_input_settings(hostapi=i)
                        found_valid_api = True
                        print(f"✓ Found working host API: {api['name']}")
                        break
                    except Exception as api_err:
                        print(f"✗ API {api['name']} not working: {api_err}")
                
                if not found_valid_api:
                    raise RuntimeError("No working audio backends found")
                
            except Exception as e:
                print(f"✗ Host API error: {e}")
                hostapis = []

            # Check for WSL environment
            in_wsl = 'WSL_DISTRO_NAME' in os.environ
            if in_wsl:
                print("\n🔍 WSL Environment Detected")
                # Check PulseAudio status
                try:
                    subprocess.run(['pulseaudio', '--version'], check=True, capture_output=True)
                    print("✓ PulseAudio installed")
                    # Check if running
                    ps_out = subprocess.run(['ps', '-e'], capture_output=True, text=True).stdout
                    if 'pulseaudio' in ps_out:
                        print("✓ PulseAudio server running")
                    else:
                        print("✗ PulseAudio server not running")
                except:
                    print("✗ PulseAudio not installed")

                # Check ALSA
                try:
                    subprocess.run(['arecord', '--version'], check=True, capture_output=True)
                    print("✓ ALSA utilities installed")
                except:
                    print("✗ ALSA utilities not installed")
            
            # Get all devices with better error handling
            try:
                devices = sd.query_devices()
                print("\n=== Available Audio Devices ===")
                for i, dev in enumerate(devices):
                    channels = f"[{dev.get('max_input_channels',0)} in, {dev.get('max_output_channels',0)} out]"
                    print(f"Device {i}: {dev.get('name', 'Unknown')} {channels}")
            except Exception as e:
                print(f"✗ Error querying devices: {e}")
                devices = []
            
            # Filter and test input devices
            input_devices = []
            for idx, device in enumerate(devices):
                try:
                    if device.get('max_input_channels', 0) > 0:
                        device_name = device.get('name')
                        if device_name:  # Skip empty names
                            # Test if device can be opened
                            try:
                                sd.check_input_settings(device=idx)
                                input_devices.append((idx, device_name))
                                print(f"✓ Found working input device: {idx} - {device_name}")
                            except Exception as dev_err:
                                print(f"✗ Device {device_name} not working: {dev_err}")
                except Exception as e:
                    print(f"✗ Error checking device {idx}: {e}")
            
            # Clear and repopulate combo box
            self.device_combo.clear()
            
            # Add devices to combo box
            for idx, name in input_devices:
                self.device_combo.addItem(name, userData=idx)
            
            # Try to select default input device
            try:
                default_device = sd.query_devices(kind='input')
                if default_device:
                    default_name = default_device.get('name')
                    if default_name:
                        print(f"✓ Default input device: {default_name}")
                        # Find and select default
                        for i in range(self.device_combo.count()):
                            if default_name in self.device_combo.itemText(i):
                                self.device_combo.setCurrentIndex(i)
                                break
            except Exception as e:
                print(f"Error getting default device: {e}")
                # If no default, select first device
                if self.device_combo.count() > 0:
                    self.device_combo.setCurrentIndex(0)
            
            if self.device_combo.count() == 0:
                self.set_validation_state(ValidationState.ERROR, "No audio input devices found")
                self.status_label.setText("❌ No audio input devices found. Please check your microphone connection.")
                self.status_label.setStyleSheet("color: #D32F2F;")
                
                # Show more detailed error message
                from qfluentwidgets import MessageBox
                msg = MessageBox(
                    "No Audio Devices Found",
                    "Could not detect any microphones.\n\n"
                    "Troubleshooting steps:\n"
                    "1. Check if your microphone is plugged in\n"
                    "2. Try unplugging and reconnecting\n"
                    "3. Check Windows sound settings\n"
                    "4. Try a different USB port\n"
                    "5. Right-click the speaker icon and select 'Open Sound settings'",
                    self
                )
                msg.exec()
            else:
                self.set_validation_state(ValidationState.INVALID, "Please test your microphone")
                status = f"✓ Found {self.device_combo.count()} audio device(s)"
                self.status_label.setText(status)
                self.status_label.setStyleSheet("color: #388E3C;")
                    
        except Exception as e:
            self.set_validation_state(ValidationState.ERROR, f"Error scanning devices: {str(e)}")
            self.status_label.setText(f"⚠️ Error loading devices: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
    
    def _on_device_selected(self, index: int):
        """Handle device selection change."""
        if index >= 0:
            self.selected_device = self.device_combo.currentData()
            self.test_button.setEnabled(True)
            self.device_test_passed = False  # Reset test status
            self.status_label.setText(f"✓ Device selected: {self.device_combo.currentText()}")
            self.status_label.setStyleSheet("color: #388E3C;")
            self.set_validation_state(ValidationState.INVALID, "Please test your microphone before proceeding")
        else:
            self.selected_device = None
            self.test_button.setEnabled(False)
            self.device_test_passed = False
            self.set_validation_state(ValidationState.INVALID, "Please select an audio device")
    
    def _test_recording(self):
        """Test recording from the selected device."""
        if self.is_recording:
            return
            
        try:
            self.is_recording = True
            self.test_button.setEnabled(False)
            self.status_label.setText("🎙️ Recording... Speak now!")
            self.status_label.setStyleSheet("color: #1976D2;")
            self.audio_data = []
            
            # Start level visualization timer
            self.level_timer.start(100)  # Update every 100ms
            
            # Record for 3 seconds with timeout protection
            duration = 3  # seconds
            
            import threading
            import queue
            
            recording_error = queue.Queue()
            recording_complete = threading.Event()
            
            def record_thread():
                try:
                    # Get device info to use native settings
                    try:
                        device_info = sd.query_devices(self.selected_device)
                        print(f"\nTesting device: {device_info}")
                        
                        # Use device's native sample rate and channels
                        sample_rate = int(device_info['default_samplerate'])
                        channels = min(1, device_info['max_input_channels'])
                        print(f"Using sample_rate={sample_rate}, channels={channels}")
                        
                    except Exception as e:
                        print(f"Error getting device info: {e}, using defaults")
                        sample_rate = 16000
                        channels = 1
                    
                    def audio_callback(indata, frames, time, status):
                        """Callback for audio input."""
                        if status:
                            print(f"Audio callback status: {status}")
                        amplitude = np.abs(indata).mean()
                        print(f"Audio level: {amplitude:.6f}")
                        self.audio_data.append(indata.copy())
                    
                    # Try to open stream with device settings
                    print(f"Opening input stream...")
                    with sd.InputStream(
                        device=self.selected_device,
                        channels=channels,
                        samplerate=sample_rate,
                        callback=audio_callback,
                        blocksize=1024,
                        latency='high'  # More stable in WSL
                    ) as stream:
                        print("Stream opened successfully")
                        print("Recording started...")
                        sd.sleep(int(duration * 1000))
                        print("Recording finished")
                        
                except Exception as e:
                    recording_error.put(e)
                finally:
                    recording_complete.set()
            
            # Start recording in separate thread
            thread = threading.Thread(target=record_thread, daemon=True)
            thread.start()
            
            # Wait for recording with timeout (duration + 2 seconds buffer)
            if not recording_complete.wait(duration + 2):
                raise TimeoutError("Recording timed out - device may be hung")
            
            # Check for errors
            try:
                error = recording_error.get_nowait()
                raise error  # Re-raise any error from recording thread
            except queue.Empty:
                pass  # No error occurred
            
            # Stop timer
            self.level_timer.stop()
            
            # Analyze recording
            if self.audio_data and hasattr(self, 'audio_stats'):
                audio_array = np.concatenate(self.audio_data, axis=0)
                max_amplitude = np.abs(audio_array).max()
                
                # Calculate quality metrics
                avg_rms = np.mean([s['rms'] for s in self.audio_stats])
                max_peak = max([s['peak'] for s in self.audio_stats])
                signal_variance = np.var(audio_array)
                
                # Quality checks
                quality_issues = []
                
                if max_amplitude < 0.01:
                    quality_issues.append("Very low audio levels detected")
                elif max_peak > 0.95:
                    quality_issues.append("Audio clipping detected")
                    
                if avg_rms < 0.001:
                    quality_issues.append("Low signal strength")
                elif avg_rms > 0.8:
                    quality_issues.append("Signal may be too hot")
                    
                if signal_variance < 0.00001:
                    quality_issues.append("Possible constant noise or DC offset")
                
                # Analyze frequency content
                if len(audio_array) > 1000:
                    from scipy import fft
                    freqs = fft.fftfreq(len(audio_array))
                    fft_vals = np.abs(fft.fft(audio_array.flatten()))
                    if np.sum(fft_vals[freqs > 0.3]) < np.sum(fft_vals[freqs < 0.1]):
                        quality_issues.append("Mostly low frequency content - check for background noise")
                
                if not quality_issues:
                    self.device_test_passed = True
                    self.status_label.setText("✓ Test successful! Audio quality looks good.")
                    self.status_label.setStyleSheet("color: #388E3C;")
                    self.set_validation_state(ValidationState.VALID, "Microphone is working correctly")
                    
                    # Show success message with stats
                    from qfluentwidgets import InfoBar, InfoBarPosition
                    InfoBar.success(
                        title="Audio Test Successful",
                        content=f"Peak level: {max_peak:.2f}, Average RMS: {avg_rms:.3f}",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
                    
                elif quality_issues:  # Make sure this connects with the if block properly
                    self.device_test_passed = False
                    issues_text = "\n• " + "\n• ".join(quality_issues)
                    self.status_label.setText("⚠️ Audio issues detected")
                    self.status_label.setStyleSheet("color: #F57C00;")
                    
                    # Show detailed quality report
                    from qfluentwidgets import MessageBox
                    msg = MessageBox(
                        "Audio Quality Issues",
                        f"The following issues were detected:{issues_text}\n\n"
                        "Suggestions:\n"
                        "• Adjust microphone position\n"
                        "• Check microphone gain/volume\n"
                        "• Try reducing background noise\n"
                        "• Test in a quieter environment\n\n"
                        f"Technical Details:\n"
                        f"Peak Level: {max_peak:.3f}\n"
                        f"Average RMS: {avg_rms:.3f}\n"
                        f"Signal Variance: {signal_variance:.6f}",
                        self
                    )
                    msg.exec()
                    
                else:
                    # No audio detected case
                    self.device_test_passed = False
                    self.status_label.setText("⚠️ No audio detected")
                    self.status_label.setStyleSheet("color: #F57C00;")
                    
                    # Show failure message
                    from qfluentwidgets import InfoBar, InfoBarPosition
                    InfoBar.warning(
                        title="No Audio Detected",
                        content="Please check your microphone connection and settings",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
                    self.device_test_passed = False
                    self.status_label.setText("⚠️ No audio detected. Please check your microphone.")
                    self.status_label.setStyleSheet("color: #F57C00;")
                    self.set_validation_state(ValidationState.INVALID, "No audio detected during test")
            else:
                self.device_test_passed = False
                self.status_label.setText("⚠️ No audio data received.")
                self.status_label.setStyleSheet("color: #F57C00;")
                self.set_validation_state(ValidationState.ERROR, "Failed to record audio")
            
            # Reset level bar
            self.level_bar.setValue(0)
            
        except Exception as e:
            self.device_test_passed = False
            error_msg = str(e)
            self.status_label.setText(f"❌ Test failed: {error_msg}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            self.set_validation_state(ValidationState.ERROR, f"Recording test failed: {error_msg}")
            self.level_timer.stop()
            self.level_bar.setValue(0)
            
            # Show detailed error dialog
            from qfluentwidgets import MessageBox
            detailed_msg = (
                f"Recording test failed with error:\n{error_msg}\n\n"
                "Troubleshooting steps:\n"
                "1. Check if microphone is muted in Windows\n"
                "2. Try a different USB port\n"
                "3. Check Windows Sound settings:\n"
                "   • Right-click speaker icon\n"
                "   • Select 'Sound settings'\n"
                "   • Check input device permissions\n"
                "4. Try restarting your computer\n\n"
                "Technical details:\n"
                f"Device ID: {self.selected_device}\n"
                f"Device name: {self.device_combo.currentText()}\n"
                f"Error type: {type(e).__name__}"
            )
            
            msg = MessageBox(
                "Recording Test Failed",
                detailed_msg,
                self
            )
            msg.exec()
            
        finally:
            self.is_recording = False
            self.test_button.setEnabled(True)
            print("Test completed, resources cleaned up")
    
    def _update_level(self):
        """Update the audio level bar during recording."""
        if self.audio_data:
            try:
                # Get most recent audio chunk
                recent_audio = self.audio_data[-1]
                amplitude = np.abs(recent_audio).mean()
                
                # Calculate RMS and peak levels
                rms_level = np.sqrt(np.mean(recent_audio**2))
                peak_level = np.max(np.abs(recent_audio))
                
                # Monitor for clipping
                if peak_level > 0.95:  # Near clipping threshold
                    self.status_label.setText("⚠️ Audio level too high!")
                    self.status_label.setStyleSheet("color: #F57C00;")
                
                # Monitor latency
                if hasattr(self, 'last_update_time'):
                    import time
                    current_time = time.time()
                    latency = current_time - self.last_update_time
                    if latency > 0.2:  # Over 200ms latency
                        print(f"High audio latency detected: {latency*1000:.1f}ms")
                self.last_update_time = time.time()
                
                # Convert to percentage (0-100) using RMS level
                level = min(int(rms_level * 1000), 100)  # Scale up and cap at 100
                self.level_bar.setValue(level)
                
                # Store audio stats for quality check
                if not hasattr(self, 'audio_stats'):
                    self.audio_stats = []
                self.audio_stats.append({
                    'rms': rms_level,
                    'peak': peak_level,
                    'amplitude': amplitude
                })
                
            except Exception as e:
                print(f"Level update error: {e}")
                # Don't let visualization errors affect recording
                pass
    
    def validate(self) -> bool:
        """
        Validate the page.
        
        Returns:
            bool: True if a device is selected and tested
        """
        return (self.selected_device is not None and 
                self.device_test_passed and
                self.get_validation_state() != ValidationState.ERROR)
    
    def validate_async(self) -> bool:
        """
        Perform asynchronous validation if needed.
        
        Returns:
            bool: True if async validation was started
        """
        # For audio devices, we do synchronous validation
        return False
    
    def get_data(self) -> dict:
        """
        Get configuration data.
        
        Returns:
            dict: Selected audio device configuration
        """
        if self.selected_device is not None:
            return {
                'audio_device': self.device_combo.currentText(),
                'audio_device_index': self.selected_device,
                'sample_rate': 16000,
                'device_test_passed': self.device_test_passed
            }
        return {}
    
    def get_title(self) -> str:
        """Get the page title."""
        return "Audio Device Setup"
    
    def get_description(self) -> str:
        """Get the page description."""
        return "Select and test your microphone to ensure high-quality voice input."
    
    def on_page_enter(self):
        """Called when the page becomes visible."""
        # Refresh device list in case something changed
        if self.device_combo.count() == 0:
            self._populate_devices()
        else:
            # Re-validate current state
            self._trigger_validation()
    
    def on_page_leave(self):
        """Called when leaving the page."""
        # Stop any ongoing recording
        if self.is_recording:
            self.level_timer.stop()
            self.is_recording = False
            self.test_button.setEnabled(True)
        
        # Cancel any pending validation
        self._cancel_async_validation()
    
    def _check_windows_permissions(self):
        """Check Windows microphone permissions"""
        try:
            # On Windows, check registry for microphone permissions
            if os.name == 'nt':
                import winreg
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone",
                        0, winreg.KEY_READ
                    )
                    
                    value, _ = winreg.QueryValueEx(key, "Value")
                    if value.lower() != "allow":
                        from qfluentwidgets import MessageBox
                        msg = MessageBox(
                            "Microphone Access Required",
                            "This app needs permission to use your microphone.\n\n"
                            "To enable:\n"
                            "1. Open Windows Settings\n"
                            "2. Go to Privacy & Security > Microphone\n"
                            "3. Enable microphone access\n"
                            "4. Allow apps to access your microphone\n"
                            "5. Restart this application",
                            self
                        )
                        msg.exec()
                        return False
                    return True
                    
                except Exception as e:
                    print(f"Failed to check Windows permissions: {e}")
                    return True  # Assume allowed if check fails
            return True
            
        except Exception as e:
            print(f"Permission check error: {e}")
            return True
    
    def _setup_wsl_audio(self):
        """Configure audio for WSL environment"""
        try:
            # Check PulseAudio installation
            try:
                subprocess.run(['pulseaudio', '--version'], 
                             check=True, capture_output=True)
                print("✓ PulseAudio installed")
            except:
                print("✗ PulseAudio not installed")
                # Show installation instructions
                from qfluentwidgets import MessageBox
                msg = MessageBox(
                    "PulseAudio Required",
                    "Audio support in WSL requires PulseAudio.\n\n"
                    "Please run these commands in your WSL terminal:\n\n"
                    "sudo apt update\n"
                    "sudo apt install pulseaudio\n"
                    "pulseaudio --start\n\n"
                    "Then restart the application.",
                    self
                )
                msg.exec()
                return False
            
            # Check if PulseAudio is running
            ps_out = subprocess.run(['ps', '-e'], capture_output=True, text=True).stdout
            if 'pulseaudio' not in ps_out:
                print("✗ PulseAudio not running - attempting to start")
                try:
                    subprocess.run(['pulseaudio', '--start'], check=True)
                    print("✓ Started PulseAudio server")
                except Exception as e:
                    print(f"✗ Failed to start PulseAudio: {e}")
                    return False
            else:
                print("✓ PulseAudio server running")
            
            # Test audio system
            try:
                devices = sd.query_devices()
                input_found = any(d.get('max_input_channels', 0) > 0 for d in devices)
                if not input_found:
                    raise RuntimeError("No input devices found")
                print("✓ Audio system responding")
                return True
                
            except Exception as e:
                print(f"✗ Audio system test failed: {e}")
                return False
                
        except Exception as e:
            print(f"✗ WSL audio setup error: {e}")
            return False
            
    def cleanup(self):
        """Clean up page resources."""
        super().cleanup()
        
        # Stop recording if active
        if self.is_recording:
            self.level_timer.stop()
            self.is_recording = False
