"""
Scribe Application - Modern voice automation platform.

Clean break from WhisperWriter. Built for modern approaches and tech.
Phoenix rising with plugin-first architecture.
"""

import sys
import time
import logging
import re
from typing import Dict, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime

try:
    import win32gui  # type: ignore
    import win32con  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    win32gui = None
    win32con = None

from PyQt5.QtCore import QObject, QTimer, Qt, pyqtSignal as Signal
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIcon

from scribe.__version__ import __version__
from scribe.plugins import PluginRegistry
from scribe.analytics.value_calculator import ValueCalculator, TranscriptionMetrics
from scribe.core.transcription_engine import TranscriptionEngine
from scribe.core.audio_recorder import AudioRecorder
from scribe.core.hotkey_manager import HotkeyManager
from scribe.core.text_formatter import TextFormatter
from scribe.ui_fluent import ScribeMainWindow
from scribe.ui_fluent.setup_wizard import SetupWizardManager
from scribe.ui_fluent.status_popup import StatusPopup
from scribe.config.config_manager import ConfigManager
from scribe.workers import TranscriptionWorker


logger = logging.getLogger(__name__)


class ScribeApp(QObject):
    """
    Modern Scribe Application.

    Architecture:
        - Plugin-first: All features are plugins
        - Analytics-first: Track value from day 1
        - Clean separation: Core, plugins, UI, analytics
        - Testable: Each component independently testable

    Flow:
        User presses hotkey
        → AudioRecorder captures
        → TranscriptionEngine transcribes
        → Text goes to plugins for processing
        → Analytics tracks everything
        → Output to user
    """

    # Signals for UI updates
    transcription_started = Signal()
    transcription_completed = Signal(str)  # transcribed text
    transcription_failed = Signal(str)  # error message
    plugin_command_executed = Signal(str, str)  # plugin name, result

    def __init__(self):
        """Initialize Scribe application."""
        super().__init__()

        logger.info(f"Initializing Scribe v{__version__}")

        # Enable high-DPI scaling BEFORE creating QApplication
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        # Qt Application
        self.qapp = QApplication(sys.argv)
        self.qapp.setApplicationName("Scribe")
        self.qapp.setApplicationVersion(__version__)

        # Set application icon
        import os
        icon_path = os.path.join('assets', 'scribe-icon.ico')
        if os.path.exists(icon_path):
            self.qapp.setWindowIcon(QIcon(icon_path))
        else:
            # Fallback to PNG
            icon_path = os.path.join('assets', 'scribe-icon.png')
            if os.path.exists(icon_path):
                self.qapp.setWindowIcon(QIcon(icon_path))

        # Configuration
        self.config = ConfigManager()
        if not self.config.config_exists():
            logger.info("First run detected - launching setup wizard")
            if not self._run_setup_wizard():
                logger.info("Setup wizard cancelled or failed")
                sys.exit(0)
            # Reload config after wizard completes
            self.config = ConfigManager()

        # Core components
        self.transcription_engine: Optional[TranscriptionEngine] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.hotkey_manager: Optional[HotkeyManager] = None

        # Plugin system
        self.plugin_registry = PluginRegistry()

        # Analytics
        self.value_calculator = ValueCalculator()

        # UI
        self.main_window: Optional[ScribeMainWindow] = None
        self.status_popup: Optional[StatusPopup] = None

        # State
        self.is_recording = False
        self.is_transcribing = False
        self._current_context: Dict[str, Optional[str]] = {}
        self._recording_mode = "idle"  # idle | hold_candidate | toggle | manual
        self._recording_source = "manual"
        self._toggle_stop_pending = False
        self._hold_threshold = 0.25
        self._text_formatter = TextFormatter(self.config.config.ai_formatting)
        self.config.config_changed.connect(self._on_config_updated)
        self._recording_mode = "idle"  # idle | hold_candidate | toggle | manual
        self._recording_source = "manual"
        self._toggle_stop_pending = False
        self._hold_threshold = 0.25
        
        # Background worker
        self._transcription_worker: Optional[TranscriptionWorker] = None

    def initialize(self) -> bool:
        """
        Initialize all components.

        Returns:
            True if initialization successful
        """
        try:
            # Initialize transcription engine
            logger.info("Initializing transcription engine...")
            self.transcription_engine = TranscriptionEngine(self.config)
            if not self.transcription_engine.initialize():
                logger.error("Failed to initialize transcription engine")
                return False

            # Initialize audio recorder
            logger.info("Initializing audio recorder...")
            self.audio_recorder = AudioRecorder(self.config)
            self.audio_recorder.recording_started.connect(self._on_recording_started)
            self.audio_recorder.recording_stopped.connect(self._on_recording_stopped)
            self.audio_recorder.level_changed.connect(self._on_audio_level)

            # Initialize hotkey manager
            logger.info("Initializing hotkey manager...")
            self.hotkey_manager = HotkeyManager(self.config)
            self.hotkey_manager.hotkey_pressed.connect(self._on_hotkey_down)
            self.hotkey_manager.hotkey_released.connect(self._on_hotkey_up)
            self.hotkey_manager.start()

            # Load plugins
            logger.info("Loading plugins...")
            self._load_plugins()

            # Initialize UI
            logger.info("Initializing UI...")
            self.main_window = ScribeMainWindow(self.config, self.plugin_registry, self.value_calculator)
            self._connect_ui_signals()
            self._sync_transcription_insights()

            # Initialize status popup
            self.status_popup = StatusPopup()

            logger.info("Scribe initialized successfully")
            logger.info("[OK] Ready! Use 'Start Listening' button or Ctrl+Alt hotkey (global hooks may require admin privileges)")
            logger.info("[INFO] Transcribed text will appear in console and as typed output")
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            return False

    def _load_plugins(self):
        """Load and register plugins."""
        # Try to load WindowManager (Day 1 plugin) - may fail on Linux/WSL
        try:
            from scribe.plugins.window_manager import WindowManager
            window_manager = WindowManager()
            config = self.config.get_plugin_config('window_manager')
            self.plugin_registry.register_plugin(window_manager, config)
            logger.info("WindowManager plugin loaded")
        except (ImportError, NotImplementedError) as e:
            logger.warning(f"WindowManager plugin not available: {e}")

        # TODO: Load other plugins from config
        # for plugin_name in self.config.get_enabled_plugins():
        #     self._load_plugin(plugin_name)

        logger.info(f"Loaded {len(self.plugin_registry.list_plugins())} plugins")

    def _connect_ui_signals(self):
        """Connect UI signals to app logic."""
        if not self.main_window:
            return

        # Connect window signals
        self.main_window.start_listening_requested.connect(self._start_listening)
        self.main_window.stop_listening_requested.connect(self._stop_listening)
        self.main_window.test_audio_requested.connect(self._test_audio_recording)
        self.main_window.settings_requested.connect(self._show_settings)
        
        # Connect transcription page signals
        if hasattr(self.main_window, 'transcription_page'):
            self.main_window.transcription_page.start_recording.connect(self._start_recording)
            self.main_window.transcription_page.stop_recording.connect(self._stop_recording)

        # Connect app signals to UI
        self.transcription_started.connect(self.main_window.on_transcription_started)
        self.transcription_completed.connect(self.main_window.on_transcription_completed)
        self.transcription_failed.connect(self.main_window.on_transcription_failed)

        # Set initial status
        self.main_window.update_hotkey_status(False)
        self.main_window.update_recording_status(False)
        self.main_window.update_transcription_status("idle")

    # ==================== Hotkey & Recording ====================

    def _on_hotkey_down(self):
        """Handle hotkey press (keys down)."""
        logger.info("[MIC] HOTKEY HANDLER CALLED!")
        print("[MIC] HOTKEY HANDLER CALLED!")

        if self.main_window:
            self.main_window.update_hotkey_status(True)
            QTimer.singleShot(300, lambda: self.main_window.update_hotkey_status(False))

        if self._recording_mode == "toggle" and self.is_recording:
            self._toggle_stop_pending = True
            return

        if self.is_recording:
            return

        self._toggle_stop_pending = False
        self._recording_mode = "hold_candidate"
        logger.info("▶️  Starting recording...")
        print("▶️  Starting recording...")
        self._start_recording(source="hotkey")

    def _on_hotkey_up(self, hold_duration: float):
        """Handle hotkey release (keys up)."""
        if self._recording_mode == "toggle" and self._toggle_stop_pending and self.is_recording:
            self._toggle_stop_pending = False
            self._recording_mode = "idle"
            logger.info("⏹️  Stopping recording (toggle tap)...")
            print("⏹️  Stopping recording...")
            self._stop_recording()
            return

        if not self.is_recording or self._recording_mode == "manual":
            self._recording_mode = "idle"
            return

        if self._recording_mode == "hold_candidate":
            if hold_duration >= self._hold_threshold:
                logger.info("⏹️  Stopping recording (hold release)...")
                print("⏹️  Stopping recording...")
                self._recording_mode = "idle"
                self._stop_recording()
            else:
                # Promote to toggle mode (continue recording)
                self._recording_mode = "toggle"
        elif self._recording_mode == "toggle":
            # Release without pending stop; keep recording
            pass

    def _start_listening(self):
        """Start listening for hotkey."""
        if self.hotkey_manager:
            self.hotkey_manager.start()
            logger.info("Started listening for hotkey")

    def _stop_listening(self):
        """Stop listening for hotkey."""
        if self.hotkey_manager:
            self.hotkey_manager.stop()
            logger.info("Stopped listening for hotkey")

    def _start_recording(self, source: str = "manual"):
        """Start audio recording."""
        if not self.audio_recorder or self.is_recording:
            return

        try:
            self._current_context = self._capture_context()

            if source == "manual":
                self._recording_mode = "manual"
            self._recording_source = source

            logger.info("[MIC] Starting recording...")
            print("[MIC] Starting recording...")
            self.is_recording = True

            # Update UI
            if self.main_window:
                self.main_window.update_recording_status(True)

            # Show status popup
            if self.status_popup:
                self.status_popup.show_recording()

            self.audio_recorder.start_recording()
            
        except Exception as e:
            # Catch any errors during recording start
            logger.error(f"Failed to start recording: {e}", exc_info=True)
            self.is_recording = False
            self._recording_mode = "idle"
            
            # Update UI to reflect error
            if self.main_window:
                self.main_window.update_recording_status(False)
            if self.status_popup:
                self.status_popup.hide()
            
            # Show error to user
            from qfluentwidgets import InfoBar, InfoBarPosition
            if self.main_window:
                InfoBar.error(
                    title="Recording Failed",
                    content=f"Failed to start recording: {str(e)}",
                    parent=self.main_window,
                    duration=5000,
                    position=InfoBarPosition.TOP_RIGHT
                )

    def _stop_recording(self):
        """Stop audio recording and trigger transcription."""
        if not self.audio_recorder or not self.is_recording:
            return

        logger.info("⏹️  Stopping recording...")
        print("⏹️  Stopping recording...")
        self.is_recording = False
        self._recording_mode = "idle"
        self._recording_source = "manual"
        self._toggle_stop_pending = False

        # Update UI
        if self.main_window:
            self.main_window.update_recording_status(False)

        audio_data = self.audio_recorder.stop_recording()

        if audio_data:
            self._transcribe_audio(audio_data)
        else:
            logger.warning("[ERROR] No audio data captured")
            print("[ERROR] No audio data captured")
            if self.status_popup:
                self.status_popup.show_error("No audio captured")
                QTimer.singleShot(2000, self.status_popup.close)

    def _test_audio_recording(self):
        """Test audio recording with a 3-second sample."""
        import threading

        def test_record():
            logger.info("[MIC] Testing audio: Recording for 3 seconds...")
            print("[MIC] Testing audio: Recording for 3 seconds...")

            if not self.audio_recorder:
                logger.error("Audio recorder not initialized")
                return

            # Start recording
            self.audio_recorder.start_recording()

            # Wait 3 seconds
            import time
            time.sleep(3)

            # Stop recording
            audio_data = self.audio_recorder.stop_recording()

            if audio_data and len(audio_data) > 0:
                logger.info(f"[OK] Audio test successful! Recorded {len(audio_data)} bytes")
                print(f"[OK] Audio test successful! Recorded {len(audio_data)} bytes")

                # Try to transcribe it
                if self.transcription_engine:
                    self._transcribe_audio(audio_data)
            else:
                logger.error("[ERROR] Audio test failed - no audio data captured")
                print("[ERROR] Audio test failed - no audio data captured")

        # Run in background thread
        thread = threading.Thread(target=test_record, daemon=True)
        thread.start()

    def _on_config_updated(self, section: str):
        """Refresh helpers when configuration changes."""
        if section == "ai_formatting":
            self._text_formatter.update_config(self.config.config.ai_formatting)
        elif section == "whisper":
            self._reload_transcription_engine()
        elif section == "audio" and self.audio_recorder:
            audio_cfg = self.config.config.audio
            self.audio_recorder.set_sample_rate(audio_cfg.sample_rate)
            self.audio_recorder.set_device(audio_cfg.device_id)

    def _reload_transcription_engine(self):
        if not self.transcription_engine:
            return
        logger.info("Reloading transcription engine with new configuration...")
        
        # Check if model is already downloaded
        model_name = self.config.config.whisper.model
        from pathlib import Path
        model_dir = Path("models") / f"models--Systran--faster-whisper-{model_name}"
        is_cached = model_dir.exists() and (model_dir / "snapshots").exists()
        
        # Show loading indicator with appropriate message
        from qfluentwidgets import StateToolTip
        if is_cached:
            message = f"Loading {model_name} model from cache..."
            logger.info(f"Model {model_name} found in cache")
        else:
            message = f"Downloading {model_name} model (first time)..."
            logger.info(f"Model {model_name} not cached, will download")
        
        self.model_loading_tip = StateToolTip("Switching Model", message, self.main_window)
        self.model_loading_tip.move(self.model_loading_tip.getSuitablePos())
        self.model_loading_tip.show()
        
        # Load model in background thread to avoid blocking UI
        def load_model_background():
            try:
                new_engine = TranscriptionEngine(self.config)
                success = new_engine.initialize()
                
                # Update UI on main thread
                from PyQt5.QtCore import QTimer
                if success:
                    QTimer.singleShot(0, lambda: self._on_model_loaded(new_engine, model_name, is_cached))
                else:
                    QTimer.singleShot(0, lambda: self._on_model_load_failed("Initialization failed"))
            except Exception as e:
                logger.error(f"Unable to reload transcription engine: {e}", exc_info=True)
                QTimer.singleShot(0, lambda: self._on_model_load_failed(str(e)))
        
        import threading
        thread = threading.Thread(target=load_model_background, daemon=True)
        thread.start()
    
    def _on_model_loaded(self, new_engine, model_name: str, was_cached: bool):
        """Called when model loading completes successfully."""
        self.transcription_engine = new_engine
        
        if was_cached:
            logger.info(f"Model '{model_name}' loaded from cache successfully")
            success_msg = f"✅ Model '{model_name}' ready (from cache)"
        else:
            logger.info(f"Model '{model_name}' downloaded and loaded successfully")
            success_msg = f"✅ Model '{model_name}' downloaded and ready"
        
        # Hide loading indicator and show success
        if hasattr(self, 'model_loading_tip'):
            self.model_loading_tip.setContent(success_msg)
            self.model_loading_tip.setState(True)
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, self.model_loading_tip.close)
    
    def _on_model_load_failed(self, error_msg: str):
        """Called when model loading fails."""
        logger.error(f"Failed to reload transcription engine: {error_msg}")
        
        # Hide loading indicator and show error
        if hasattr(self, 'model_loading_tip'):
            self.model_loading_tip.setContent(f"❌ Model load failed: {error_msg}")
            self.model_loading_tip.setState(False)
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(3000, self.model_loading_tip.close)

    def _on_recording_started(self):
        """Callback when recording starts."""
        logger.debug("Recording started")

    def _on_recording_stopped(self, audio_data):
        """Callback when recording stops."""
        logger.debug(f"Recording stopped: {len(audio_data)} bytes")

    def _on_audio_level(self, level: float):
        """Forward audio level updates to UI."""
        if self.main_window:
            self.main_window.update_audio_level(level)

    # ==================== Transcription ====================

    def _transcribe_audio(self, audio_data):
        """
        Transcribe audio in background thread (non-blocking).
        
        Uses QThread worker to keep UI responsive during 2-3 second transcription.
        
        Args:
            audio_data: Audio bytes to transcribe
        """
        if not self.transcription_engine or self.is_transcribing:
            return

        logger.info("[TRANSCRIBING] Starting transcription in background...")
        print("[TRANSCRIBING] Transcribing audio...")
        self.is_transcribing = True

        # Show transcribing status
        if self.status_popup:
            self.status_popup.show_transcribing()
        self.transcription_started.emit()

        # Cancel any existing worker
        if self._transcription_worker and self._transcription_worker.isRunning():
            logger.warning("Cancelling previous transcription worker")
            self._transcription_worker.cancel()
            self._transcription_worker.wait()

        # Create and configure worker
        self._transcription_worker = TranscriptionWorker(
            self.transcription_engine,
            audio_data
        )
        
        # Connect signals
        self._transcription_worker.transcription_complete.connect(
            self._on_transcription_complete
        )
        self._transcription_worker.transcription_failed.connect(
            self._on_transcription_failed
        )
        
        # Start transcription in background
        self._transcription_worker.start()
        logger.info("✅ Transcription worker started - UI remains responsive!")
    
    def _on_transcription_complete(self, result):
        """
        Handle successful transcription completion.
        
        This runs in the main thread (safe to update UI).
        """
        try:
            import time
            
            raw_text = result.text.strip()
            formatted_text = self._format_transcription(raw_text)
            ai_formatted = bool(formatted_text and formatted_text != raw_text)
            text = formatted_text or raw_text
            word_count = len(text.split())
            
            logger.debug(f"[RAW] Transcription: '{raw_text}'")
            if ai_formatted:
                logger.debug(f"[AI] Formatted to: '{text}'")
            logger.info(f"[OK] Transcription: '{text}' ({word_count} words)")
            print(f"\n{'='*60}")
            print(f"[OK] TRANSCRIPTION RESULT:")
            print(f"{'='*60}")
            print(f"{text}")
            print(f"{'='*60}\n")

            # Check if this is a voice command
            is_command, used_plugin = self._process_as_command(text)

            context = self._current_context or {}

            # Track analytics
            metrics = self.value_calculator.record_transcription(
                audio_duration=result.duration or 1.0,
                word_count=word_count,
                transcription_time=0.0,  # Worker doesn't track timing yet
                was_command=is_command,
                confidence=result.confidence,
                language=result.language,
                application=context.get("application"),
                window_title=context.get("window_title"),
                window_handle=context.get("window_handle"),
                text=text,
                character_count=len(text)
            )

            summary = self.value_calculator.get_session_summary()

            if not is_command:
                # Regular transcription - emit to UI
                self.transcription_completed.emit(text)
                # Always try to return text to original app if we have context
                if context and context.get("window_handle"):
                    logger.info("Attempting to paste transcription back to originating app...")
                    self._return_text_to_application(text, context)
                else:
                    logger.info("No window context captured - transcription stays in Scribe UI only")

            # Push analytics to UI
            if self.main_window:
                self.main_window.update_transcription_summary(summary)
                history_entry = self._build_history_entry(metrics)
                history_entry["text"] = text
                history_entry["raw_text"] = raw_text if ai_formatted else text
                history_entry["ai_formatted"] = ai_formatted
                history_entry["used_plugin"] = used_plugin
                
                # Add audio file path for playback
                audio_file = Path("data/audio") / f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                latest_recording = Path("data/audio/latest_recording.wav")
                if latest_recording.exists():
                    history_entry["audio_file"] = str(latest_recording.absolute())
                
                self.main_window.add_transcription_event(history_entry)

            # Show complete status briefly
            if self.status_popup:
                self.status_popup.show_complete()
                QTimer.singleShot(1500, self.status_popup.close)

        except Exception as e:
            logger.error(f"[ERROR] Failed to process transcription result: {e}", exc_info=True)
            self._on_transcription_failed(str(e))
        
        finally:
            self.is_transcribing = False
            self._current_context = {}
    
    def _on_transcription_failed(self, error_message: str):
        """
        Handle transcription failure.
        
        This runs in the main thread (safe to update UI).
        """
        logger.warning(f"[ERROR] Transcription failed: {error_message}")
        print(f"[ERROR] {error_message}")
        
        self.transcription_failed.emit(error_message)

        if self.status_popup:
            # Show full error message (status popup is now wider to accommodate)
            self.status_popup.show_error(f"Error: {error_message}")
            QTimer.singleShot(2000, self.status_popup.close)
        
        self.is_transcribing = False
        self._current_context = {}

    def _capture_context(self) -> Dict[str, Optional[str]]:
        """Capture the currently active window/application for telemetry."""
        context: Dict[str, Optional[str]] = {
            "application": None,
            "window_title": None,
            "window_handle": None,
        }
        handle = None

        if sys.platform.startswith("win") and win32gui:
            try:
                handle = win32gui.GetForegroundWindow()
                if handle:
                    context["window_handle"] = int(handle)
            except Exception as e:
                logger.debug(f"Unable to capture window handle via win32gui: {e}")

        try:
            import pygetwindow as gw  # type: ignore

            window = gw.getActiveWindow()
            if window and getattr(window, "title", None):
                title = window.title.strip()
                context["window_title"] = title
                context["application"] = self._extract_application_name(title)
                if not handle:
                    handle_attr = getattr(window, "_hWnd", None)
                    if handle_attr:
                        context["window_handle"] = int(handle_attr)
        except Exception as e:
            logger.debug(f"Unable to capture active window title: {e}")
        logger.debug(
            "Captured context: title='%s', handle=%s",
            context.get("window_title"),
            context.get("window_handle"),
        )
        return context

    @staticmethod
    def _extract_application_name(title: Optional[str]) -> Optional[str]:
        """Best-effort extraction of app name from a window title."""
        if not title:
            return None
        if " - " in title:
            return title.split(" - ")[-1].strip()
        if " | " in title:
            return title.split(" | ")[-1].strip()
        return title.strip()

    def _build_history_entry(self, metrics: TranscriptionMetrics) -> Dict[str, Any]:
        """Convert transcription metrics into a UI-friendly dict."""
        return {
            "timestamp": metrics.timestamp,
            "application": metrics.application or metrics.window_title or "Unknown app",
            "window_title": metrics.window_title,
            "window_handle": metrics.window_handle,
            "audio_duration": metrics.audio_duration,
            "word_count": metrics.word_count,
            "character_count": metrics.character_count,
            "confidence": metrics.confidence,
            "language": metrics.language,
            "text": metrics.text,
        }

    def _format_transcription(self, raw_text: str) -> str:
        """Apply AI-style cleanup according to configuration."""
        if not hasattr(self, "_text_formatter") or self._text_formatter is None:
            self._text_formatter = TextFormatter(self.config.config.ai_formatting)
        return self._text_formatter.format_text(raw_text)

    def _return_text_to_application(self, text: str, context: Dict[str, Any]):
        """Attempt to switch back to the originating window and paste the transcription."""
        if not context or not text:
            logger.warning("No context or text to return")
            return

        window_handle = context.get("window_handle")
        window_title = context.get("window_title")
        
        # Don't refocus if the target window is Scribe itself - but still copy to clipboard
        if window_title and "Scribe" in window_title:
            logger.info(f"Target window is Scribe itself - skipping auto-paste (text available in History tab)")
            # Still copy to clipboard for manual paste
            try:
                import pyperclip
                pyperclip.copy(text)
                logger.info("✅ Text copied to clipboard (paste manually with Ctrl+V)")
            except Exception as e:
                logger.warning(f"Failed to copy to clipboard: {e}")
            return
        
        logger.info(f"Attempting to return text to: title='{window_title}', handle={window_handle}")

        restored = False

        # Try win32 API first (most reliable on Windows)
        if window_handle and self._activate_window_by_handle(window_handle):
            logger.info("✅ Window activated via handle")
            restored = True

        # Fallback to pygetwindow
        if not restored and window_title:
            try:
                import pygetwindow as gw  # type: ignore

                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    logger.info(f"Found {len(windows)} window(s) matching title, activating first...")
                    windows[0].activate()
                    restored = True
                    logger.info("✅ Window activated via pygetwindow")
                else:
                    logger.warning(f"No windows found with title: {window_title}")
            except ImportError:
                logger.warning("pygetwindow not installed - cannot use title-based window activation")
            except Exception as e:
                logger.warning(f"pygetwindow fallback failed: {e}")

        if restored:
            logger.info(
                "Refocused target window title='%s' handle=%s",
                context.get("window_title"), context.get("window_handle")
            )
            # Longer delay to ensure window is fully activated and ready for input
            logger.debug("Waiting 0.5s for window to be ready...")
            time.sleep(0.5)
            if not self._inject_text_into_app(text):
                logger.error("❌ Failed to insert text into active window; check clipboard permissions.")
                if self.status_popup:
                    self.status_popup.show_error("Unable to insert text")
                    QTimer.singleShot(1500, self.status_popup.close)
            else:
                logger.info("✅ Text successfully returned to application!")
        else:
            logger.warning(f"❌ Could not refocus original window '{window_title}'; leaving text in Scribe output.")
            if self.status_popup:
                self.status_popup.show_error("Unable to focus target app")
                QTimer.singleShot(1500, self.status_popup.close)

    def _inject_text_into_app(self, text: str) -> bool:
        """Insert text into the focused window using configured mode."""
        # Apply smart formatting (spacing and capitalization)
        text = self._smart_format_text(text)
        
        mode = getattr(self.config.config.post_processing, "auto_insert_mode", "paste")
        mode = mode.lower()
        logger.info("Attempting to insert text via mode='%s'", mode)
        if mode == "paste":
            return self._paste_via_clipboard(text)
        if mode == "type":
            return self._type_via_keystrokes(text)
        if mode == "both":
            return self._paste_via_clipboard(text) or self._type_via_keystrokes(text)
        return False
    
    def _smart_format_text(self, text: str) -> str:
        """Apply smart formatting: spacing and capitalization based on context"""
        if not text or not text.strip():
            return text
        
        try:
            import pyautogui
            import pyperclip
            
            pyautogui.FAILSAFE = False
            
            # Get context by reading characters before cursor
            # Save current clipboard
            saved_clipboard = pyperclip.paste()
            
            # Select word/chars before cursor with Shift+Ctrl+Left, then Ctrl+C
            pyperclip.copy("")
            time.sleep(0.03)
            
            # Try Shift+Home to get line content before cursor
            pyautogui.hotkey('shift', 'home')
            time.sleep(0.03)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.05)
            
            before_text = pyperclip.paste()
            
            # Deselect (Right arrow)
            pyautogui.press('right')
            time.sleep(0.02)
            
            # Restore clipboard
            pyperclip.copy(saved_clipboard)
            
            # Analyze context
            needs_capital = False
            needs_space = False
            
            if before_text:
                # Check if we need a leading space
                if before_text and not before_text[-1].isspace():
                    needs_space = True
                
                # Check if we need capitalization (start of sentence)
                stripped = before_text.rstrip()
                if not stripped or stripped[-1] in '.!?':
                    needs_capital = True
            else:
                # No text before cursor - assume start of document/field
                needs_capital = True
            
            # Apply formatting
            formatted = text
            if needs_capital and formatted[0].islower():
                formatted = formatted[0].upper() + formatted[1:]
            
            if needs_space:
                formatted = ' ' + formatted
            
            logger.debug(f"Smart format: '{text}' -> '{formatted}' (capital={needs_capital}, space={needs_space})")
            return formatted
            
        except Exception as e:
            logger.warning(f"Smart formatting failed: {e}, using original text")
            return text

    def _paste_via_clipboard(self, text: str) -> bool:
        try:
            import pyautogui
            import pyperclip
        except ImportError as e:
            logger.warning(f"Cannot insert text (missing dependency): {e}")
            # Try to at least copy to clipboard as backup
            try:
                import pyperclip
                pyperclip.copy(text)
                logger.info("✅ Text copied to clipboard (paste manually with Ctrl+V)")
                return True
            except:
                return False

        try:
            pyautogui.FAILSAFE = False
            
            logger.debug(f"Copying transcription to clipboard: '{text[:50]}...'")
            pyperclip.copy(text)
            
            # Give window more time to activate and cursor to stabilize
            time.sleep(0.2)
            
            logger.debug("Simulating Ctrl+V...")
            pyautogui.hotkey('ctrl', 'v')
            
            # Wait for paste to complete
            time.sleep(0.15)
            logger.info("✅ Inserted text via clipboard paste (text remains in clipboard for re-paste)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to paste text: {e}")
            # Text is already in clipboard from above, so partial success
            logger.info("✅ Text is in clipboard - paste manually with Ctrl+V")
            return True  # Return True since clipboard has the text

    def _type_via_keystrokes(self, text: str) -> bool:
        try:
            import pyautogui
        except ImportError as e:
            logger.warning(f"Cannot type text (missing dependency): {e}")
            return False

        try:
            pyautogui.FAILSAFE = False
            delay = getattr(self.config.config.post_processing, "writing_key_press_delay", 0.002)
            pyautogui.typewrite(text, interval=max(0.0, min(0.1, delay)))
            logger.info("Inserted text via simulated typing")
            return True
        except Exception as e:
            logger.warning(f"Failed to type text via keystrokes: {e}")
            return False

    def _activate_window_by_handle(self, handle: int) -> bool:
        """Use win32 APIs to bring a window to the foreground."""
        if not win32gui or not win32con:
            return False

        try:
            if win32gui.IsIconic(handle):
                win32gui.ShowWindow(handle, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(handle)
            return True
        except Exception as e:
            logger.debug(f"Failed to activate window by handle: {e}")
            return False

    def _sync_transcription_insights(self):
        """Push current analytics summary/history to the UI."""
        if not self.main_window:
            return

        summary = self.value_calculator.get_session_summary()
        self.main_window.update_transcription_summary(summary)

        recent = self.value_calculator.get_recent_transcriptions()
        for metrics in recent:
            self.main_window.add_transcription_event(self._build_history_entry(metrics))

    def _process_as_command(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if text is a voice command and execute it.

        Args:
            text: Transcribed text

        Returns:
            Tuple of (is_command: bool, plugin_name: Optional[str])
        """
        # Simple command detection: Check if text matches any registered pattern
        # TODO: Improve with intent classification

        text_lower = text.lower().strip()

        # Try to find matching command
        for pattern, commands in self.plugin_registry._commands.items():
            # Pattern matching with parameter extraction
            matched, params = self._pattern_matches(text_lower, pattern)
            
            if matched:
                command = commands[0]  # Use first matching command
                plugin_name = command.plugin.name

                try:
                    import time
                    start_time = time.time()

                    # Execute command with extracted parameters
                    logger.info(f"Executing command: {pattern} via {plugin_name} with params: {params}")
                    
                    # Call handler with extracted parameters as keyword arguments
                    result = command.handler(**params)
                    execution_time = time.time() - start_time

                    # Track analytics
                    self.value_calculator.record_command(
                        command_pattern=pattern,
                        plugin=plugin_name,
                        execution_time=execution_time,
                        success=True
                    )

                    # Emit to UI
                    self.plugin_command_executed.emit(plugin_name, str(result))

                    logger.info(f"Command executed successfully: {result}")
                    return True, plugin_name

                except Exception as e:
                    logger.error(f"Command execution failed: {e}")
                    self.value_calculator.record_command(
                        command_pattern=pattern,
                        plugin=plugin_name,
                        execution_time=0,
                        success=False,
                        error_message=str(e)
                    )
                    return False, plugin_name

        return False, None

    def _pattern_matches(self, text: str, pattern: str) -> Tuple[bool, Dict[str, str]]:
        """
        Template-based matching with {placeholder} variable extraction.
        
        Args:
            text: User's spoken text (transcription)
            pattern: Command pattern like "switch to {app}" or "open {file}"
            
        Returns:
            Tuple of (matched: bool, parameters: dict)
            
        Examples:
            >>> _pattern_matches("switch to chrome", "switch to {app}")
            (True, {"app": "chrome"})
            
            >>> _pattern_matches("hello world", "switch to {app}")
            (False, {})
            
            >>> _pattern_matches("open file.txt in editor", "open {file} in {app}")
            (True, {"file": "file.txt", "app": "editor"})
        """
        pattern = pattern.strip().lower()
        text = text.strip().lower()
        
        if not pattern:
            return False, {}

        # Build regex with named capture groups for placeholders
        tokens = []
        placeholder_names = []
        
        for i, part in enumerate(pattern.split()):
            if part.startswith("{") and part.endswith("}"):
                # Extract placeholder name
                name = part[1:-1]
                placeholder_names.append(name)
                
                # Check if this is the last token - if so, match everything remaining
                is_last = (i == len(pattern.split()) - 1)
                
                if is_last:
                    # Last placeholder: greedy match to end of string
                    tokens.append(rf"(?P<{name}>.+)")
                else:
                    # Middle placeholder: non-greedy match for one or more words
                    tokens.append(rf"(?P<{name}>\S+)")
            else:
                # Literal text - escape special regex characters
                tokens.append(re.escape(part))
        
        # Join with flexible whitespace matching
        regex = r"\b" + r"\s+".join(tokens) + r"\b"
        
        # Try to match
        match = re.search(regex, text)
        
        if match:
            # Extract all named groups (parameters)
            params = match.groupdict()
            # Clean up parameters - strip whitespace
            params = {k: v.strip() for k, v in params.items()}
            return True, params
        else:
            return False, {}

    # ==================== UI Actions ====================

    def _show_settings(self):
        """Show settings window."""
        logger.info("Opening settings window...")
        from scribe.ui.settings_window import SettingsWindow

        settings_dialog = SettingsWindow(self.config, parent=self.main_window)
        settings_dialog.exec_()  # Show as modal dialog

    def _run_setup_wizard(self) -> bool:
        """
        Run the first-time setup wizard.
        
        Returns:
            True if wizard completed successfully, False if cancelled
        """
        logger.info("Starting setup wizard...")
        
        # Create and configure wizard
        wizard = SetupWizardManager()
        
        # Connect wizard signals
        wizard.wizard_completed.connect(self._on_wizard_completed)
        wizard.wizard_cancelled.connect(self._on_wizard_cancelled)
        
        # Show wizard and wait for completion
        result = wizard.exec()
        
        return result == QDialog.DialogCode.Accepted
    
    def _on_wizard_completed(self, wizard_data: dict):
        """
        Handle wizard completion.
        
        Args:
            wizard_data: Configuration data collected from wizard
        """
        logger.info(f"Setup wizard completed with data: {wizard_data}")
        
        # Save configuration
        try:
            # Update config with wizard data
            if 'audio_device' in wizard_data:
                self.config.config.audio.device_index = wizard_data['audio_device']
            
            if 'hotkey' in wizard_data:
                self.config.config.hotkeys.toggle_recording = wizard_data['hotkey']
            
            # Save to file
            self.config.save()
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save wizard configuration: {e}", exc_info=True)
    
    def _on_wizard_cancelled(self):
        """Handle wizard cancellation."""
        logger.info("Setup wizard was cancelled")

    # ==================== Application Lifecycle ====================

    def run(self) -> int:
        """
        Run the application.

        Returns:
            Exit code
        """
        if not self.initialize():
            logger.error("Failed to initialize Scribe")
            return 1

        # Show and activate main window
        if self.main_window:
            logger.info("Showing main window...")
            self.main_window.showNormal()  # Show in normal state (not minimized/maximized)
            self.main_window.raise_()  # Bring to front
            self.main_window.activateWindow()  # Make it active
            logger.info(f"Window visible: {self.main_window.isVisible()}")
            logger.info(f"Window geometry: {self.main_window.geometry()}")

        logger.info("Scribe running...")

        # Run Qt event loop
        return self.qapp.exec_()

    def shutdown(self):
        """Shutdown application and cleanup resources."""
        logger.info("Shutting down Scribe...")

        # Cancel any running transcription worker
        if self._transcription_worker and self._transcription_worker.isRunning():
            logger.info("Stopping transcription worker...")
            self._transcription_worker.cancel()
            self._transcription_worker.wait(5000)  # Wait up to 5 seconds

        # Stop listening
        if self.hotkey_manager:
            self.hotkey_manager.stop()

        # Shutdown plugins
        self.plugin_registry.shutdown_all()

        # Save analytics
        self.value_calculator.save_session()

        # Print session summary
        summary = self.value_calculator.get_session_summary()
        self.value_calculator.print_summary(summary)

        logger.info("Scribe shutdown complete")
