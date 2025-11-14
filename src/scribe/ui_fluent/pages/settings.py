"""
Settings Page - Configuration interface with ConfigManager integration
"""

import logging
from PyQt5.QtCore import pyqtSignal as Signal, QThread, QEvent, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QApplication, QDialog
from PyQt5.QtGui import QKeyEvent
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel,
    CardWidget, SwitchButton, ComboBox, PrimaryPushButton, PushButton,
    FluentIcon as FIF, setTheme, Theme, setThemeColor,
    InfoBar, InfoBarPosition, MessageBox
)

from scribe.config import ConfigManager

logger = logging.getLogger(__name__)


class SettingsPage(ScrollArea):
    """Settings page with real config persistence"""
    
    config_changed = Signal(str)
    
    def __init__(self, config_manager: ConfigManager = None, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage")
        
        self.config_manager = config_manager or ConfigManager()
        
        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        
        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)
        self.vBoxLayout.setSpacing(20)
        
        title = TitleLabel("Settings")
        
        # Sections
        general_card = self._create_general_settings()
        audio_card = self._create_audio_settings()
        whisper_card = self._create_whisper_settings()
        appearance_card = self._create_appearance_settings()
        logs_card = self._create_logs_settings()
        
        self.vBoxLayout.addWidget(title)
        self.vBoxLayout.addWidget(SubtitleLabel("General"))
        self.vBoxLayout.addWidget(general_card)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(SubtitleLabel("Audio"))
        self.vBoxLayout.addWidget(audio_card)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(SubtitleLabel("Whisper Model"))
        self.vBoxLayout.addWidget(whisper_card)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(SubtitleLabel("Appearance"))
        self.vBoxLayout.addWidget(appearance_card)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(SubtitleLabel("Logs & Debugging"))
        self.vBoxLayout.addWidget(logs_card)
        
        self.vBoxLayout.addStretch(1)
        
        # Load initial values from config
        self._load_from_config()
        
        # Connect auto-save handlers (after loading to avoid spurious saves)
        self._connect_auto_save_handlers()
    
    def _create_general_settings(self):
        from qfluentwidgets import LineEdit, StrongBodyLabel

        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Hotkey configuration - IMPROVED UI
        hotkey_section = SubtitleLabel("Recording Hotkey")
        hotkey_section.setStyleSheet("font-weight: bold; color: #4CAF50;")

        # Hotkey capture button row
        hotkey_row = QHBoxLayout()
        hotkey_label = StrongBodyLabel("Press to record hotkey:")
        hotkey_label.setStyleSheet("font-size: 11px;")  # Reduced from 12px (10% smaller)
        
        # Hotkey display/capture button (10% smaller: 200->180, 40->36)
        self.hotkey_button = PushButton("Click to Set Hotkey")
        self.hotkey_button.setFixedWidth(180)
        self.hotkey_button.setFixedHeight(36)
        self.hotkey_button.clicked.connect(self._capture_hotkey)
        self.hotkey_button.setStyleSheet("""
            PushButton {
                font-size: 12px;
                font-weight: bold;
                background-color: #3A3A3A;
                border: 2px solid #4CAF50;
            }
            PushButton:hover {
                background-color: #4A4A4A;
                border: 2px solid #66BB6A;
            }
        """)
        
        # Reset button (10% smaller: 140->126)
        reset_hotkey_btn = PushButton("Reset to Default")
        reset_hotkey_btn.setFixedWidth(126)
        reset_hotkey_btn.clicked.connect(self._reset_hotkey)
        
        hotkey_row.addWidget(hotkey_label)
        hotkey_row.addStretch()
        hotkey_row.addWidget(self.hotkey_button)
        hotkey_row.addSpacing(8)
        hotkey_row.addWidget(reset_hotkey_btn)

        # Hotkey help text (10% smaller: 10px->9px)
        hotkey_help = BodyLabel("💡 Click the button above and press your desired key combination.\n⚠️ Global hotkeys require Administrator privileges on Windows.")
        hotkey_help.setStyleSheet("color: #FF9800; font-size: 9px; margin-left: 8px; margin-top: 5px;")
        hotkey_help.setWordWrap(True)

        # Current hotkey display with dark background for readability
        self.current_hotkey_label = BodyLabel("Current: Ctrl+Alt")
        self.current_hotkey_label.setStyleSheet("""
            color: #4CAF50; 
            font-size: 10px; 
            font-weight: bold; 
            margin-left: 8px; 
            margin-top: 4px;
            background-color: #2A2A2A;
            padding: 4px 8px;
            border-radius: 4px;
        """)

        # Separator
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #3F3F3F; margin: 8px 0;")

        # Minimize to tray
        tray_row = QHBoxLayout()
        tray_label = BodyLabel("Minimize to system tray")
        self.minimize_tray_switch = SwitchButton()
        tray_row.addWidget(tray_label)
        tray_row.addStretch()
        tray_row.addWidget(self.minimize_tray_switch)

        # Show system tray icon
        systray_row = QHBoxLayout()
        systray_label = BodyLabel("Show system tray icon")
        self.show_tray_switch = SwitchButton()
        systray_row.addWidget(systray_label)
        systray_row.addStretch()
        systray_row.addWidget(self.show_tray_switch)

        # Start minimized
        start_row = QHBoxLayout()
        start_label = BodyLabel("Start minimized")
        self.start_minimized_switch = SwitchButton()
        start_row.addWidget(start_label)
        start_row.addStretch()
        start_row.addWidget(self.start_minimized_switch)

        layout.addWidget(hotkey_section)
        layout.addLayout(hotkey_row)
        layout.addWidget(self.current_hotkey_label)
        layout.addWidget(hotkey_help)
        layout.addWidget(separator)
        layout.addLayout(tray_row)
        layout.addLayout(systray_row)
        layout.addLayout(start_row)

        return card
    
    def _create_audio_settings(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Device - Populate with real devices
        device_row = QHBoxLayout()
        device_label = BodyLabel("Audio Device")
        self.device_combo = ComboBox()
        
        # Load available devices
        try:
            from scribe.core.audio_recorder import AudioRecorder
            devices = AudioRecorder.list_devices()
            
            if devices:
                for device in devices:
                    label = f"{device['name']}"
                    if device['is_default']:
                        label += " (Default)"
                    self.device_combo.addItem(label, userData=device['id'])
            else:
                self.device_combo.addItem("No devices found", userData=None)
        except Exception as e:
            self.device_combo.addItem(f"Error loading devices: {e}", userData=None)
        
        self.device_combo.setFixedWidth(300)
        device_row.addWidget(device_label)
        device_row.addStretch()
        device_row.addWidget(self.device_combo)
        
        # Sample rate
        rate_row = QHBoxLayout()
        rate_label = BodyLabel("Sample Rate")
        self.rate_combo = ComboBox()
        self.rate_combo.addItem("16000 Hz (Recommended)", userData=16000)
        self.rate_combo.addItem("44100 Hz", userData=44100)
        self.rate_combo.addItem("48000 Hz", userData=48000)
        self.rate_combo.setFixedWidth(300)
        rate_row.addWidget(rate_label)
        rate_row.addStretch()
        rate_row.addWidget(self.rate_combo)
        
        # Test button
        test_row = QHBoxLayout()
        test_btn = PrimaryPushButton(FIF.MICROPHONE, "Test Microphone")
        test_btn.setFixedWidth(200)
        test_btn.clicked.connect(self._test_microphone)
        test_row.addStretch()
        test_row.addWidget(test_btn)
        test_row.addStretch()
        
        layout.addLayout(device_row)
        layout.addLayout(rate_row)
        layout.addLayout(test_row)
        
        return card
    
    def _create_whisper_settings(self):
        """Create Whisper model configuration card with detailed explanations."""
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Model info data with GPU/CPU times
        self.model_info = {
            "tiny": {
                "size": "39 MB",
                "speed": "⚡⚡⚡ Fastest",
                "quality": "⭐⭐ Fair",
                "time_cpu": "~0.5-1s",
                "time_gpu": "~0.2-0.5s",
                "pros": "Ultra-fast, minimal RAM",
                "cons": "Lower accuracy, misses words",
                "best_for": "Testing, quick drafts"
            },
            "base": {
                "size": "74 MB", 
                "speed": "⚡⚡ Very Fast",
                "quality": "⭐⭐⭐ Good",
                "time_cpu": "~1-2s",
                "time_gpu": "~0.5-1s",
                "pros": "Fast with decent accuracy",
                "cons": "Still misses some words",
                "best_for": "Quick transcriptions, clear speech"
            },
            "small": {
                "size": "244 MB",
                "speed": "⚡ Fast", 
                "quality": "⭐⭐⭐⭐ Very Good",
                "time_cpu": "~2-3s",
                "time_gpu": "~1-1.5s",
                "pros": "Balanced speed/quality",
                "cons": "May struggle with accents",
                "best_for": "Daily use, balanced performance"
            },
            "medium": {
                "size": "769 MB",
                "speed": "🐢 Slower",
                "quality": "⭐⭐⭐⭐⭐ Excellent", 
                "time_cpu": "~4-6s",
                "time_gpu": "~1.5-2s",
                "pros": "High accuracy, handles accents well",
                "cons": "Slower, more RAM (1.5GB)",
                "best_for": "Professional work, accuracy matters"
            },
            "large-v2": {
                "size": "1.5 GB",
                "speed": "🐢🐢 Slowest",
                "quality": "⭐⭐⭐⭐⭐⭐ Best",
                "time_cpu": "~8-12s",
                "time_gpu": "~3-4s",
                "pros": "Best accuracy, proper punctuation",
                "cons": "Very slow on CPU, needs 3GB RAM",
                "best_for": "Studio quality, GPU recommended"
            }
        }
        
        # Model selection row
        model_row = QHBoxLayout()
        model_label = SubtitleLabel("Transcription Model")
        model_label.setStyleSheet("font-weight: bold;")
        model_row.addWidget(model_label)
        
        # Model dropdown - WIDER for full model names
        model_select_row = QHBoxLayout()
        model_select_label = BodyLabel("Model:")
        self.model_combo = ComboBox()
        models = ["tiny", "base", "small", "medium", "large-v2"]
        for model in models:
            display_name = model.replace("-", " ").title()
            self.model_combo.addItem(display_name, userData=model)
        self.model_combo.setFixedWidth(300)  # Increased from 200
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        
        model_select_row.addWidget(model_select_label)
        model_select_row.addWidget(self.model_combo)
        model_select_row.addStretch()
        
        # Model info display (will be populated by _on_model_changed)
        self.model_info_label = BodyLabel("")
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setTextFormat(Qt.TextFormat.RichText)  # Enable HTML formatting
        self.model_info_label.setStyleSheet("""
            background-color: rgba(80, 80, 80, 0.3);
            border-radius: 8px;
            padding: 12px;
            line-height: 1.5;
            font-size: 11px;
        """)
        
        # Download button
        download_row = QHBoxLayout()
        self.download_model_btn = PrimaryPushButton(FIF.DOWNLOAD, "Download Model")
        self.download_model_btn.setFixedWidth(200)
        self.download_model_btn.clicked.connect(self._download_model)
        self.download_model_btn.setVisible(False)  # Hidden by default
        download_row.addStretch()
        download_row.addWidget(self.download_model_btn)
        download_row.addStretch()
        
        # Progress bar for download
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        self.download_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3F3F3F;
                border-radius: 4px;
                text-align: center;
                background-color: #2B2B2B;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        # Separator
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #3F3F3F; margin: 12px 0;")
        
        # Device configuration
        device_section = SubtitleLabel("Compute Settings")
        device_section.setStyleSheet("font-weight: bold; margin-top: 8px;")
        
        # Device selection
        device_row = QHBoxLayout()
        device_label = BodyLabel("Compute Device:")
        self.compute_device_combo = ComboBox()
        self.compute_device_combo.addItem("🤖 Auto (Recommended)", userData="auto")
        self.compute_device_combo.addItem("💻 CPU", userData="cpu")
        self.compute_device_combo.addItem("🚀 CUDA (NVIDIA GPU)", userData="cuda")
        self.compute_device_combo.setFixedWidth(200)
        self.compute_device_combo.currentTextChanged.connect(self._on_device_changed)
        device_row.addWidget(device_label)
        device_row.addWidget(self.compute_device_combo)
        device_row.addStretch()
        
        # Device info label
        self.device_info_label = BodyLabel("")
        self.device_info_label.setWordWrap(True)
        self.device_info_label.setStyleSheet("color: #4CAF50; font-size: 10px; margin-left: 8px;")
        
        # Compute type
        compute_row = QHBoxLayout()
        compute_label = BodyLabel("Precision:")
        self.compute_type_combo = ComboBox()
        self.compute_type_combo.addItem("INT8 (Fast, CPU)", userData="int8")
        self.compute_type_combo.addItem("Float16 (Balanced, GPU)", userData="float16")
        self.compute_type_combo.addItem("Float32 (Accurate, Slow)", userData="float32")
        self.compute_type_combo.setFixedWidth(200)
        compute_row.addWidget(compute_label)
        compute_row.addWidget(self.compute_type_combo)
        compute_row.addStretch()
        
        # Language selection
        lang_section = SubtitleLabel("Language")
        lang_section.setStyleSheet("font-size: 12px; font-weight: bold; margin-top: 8px;")
        
        lang_row = QHBoxLayout()
        lang_label = BodyLabel("Transcription Language:")
        lang_label.setFixedWidth(180)
        
        self.language_combo = ComboBox()
        self.language_combo.addItem("Auto-detect", "auto")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Spanish", "es")
        self.language_combo.addItem("French", "fr")
        self.language_combo.addItem("German", "de")
        self.language_combo.addItem("Italian", "it")
        self.language_combo.addItem("Portuguese", "pt")
        self.language_combo.addItem("Russian", "ru")
        self.language_combo.addItem("Chinese", "zh")
        self.language_combo.addItem("Japanese", "ja")
        self.language_combo.addItem("Korean", "ko")
        self.language_combo.addItem("Arabic", "ar")
        self.language_combo.addItem("Hindi", "hi")
        self.language_combo.addItem("Dutch", "nl")
        self.language_combo.addItem("Polish", "pl")
        self.language_combo.addItem("Turkish", "tr")
        self.language_combo.setFixedWidth(200)
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
        
        lang_row.addWidget(lang_label)
        lang_row.addWidget(self.language_combo)
        lang_row.addStretch()
        
        lang_info = BodyLabel("💡 Specify your language for 10-15% faster transcription")
        lang_info.setStyleSheet("color: #FF9800; font-size: 10px; font-style: italic;")
        
        # Add all to layout
        layout.addLayout(model_row)
        layout.addLayout(model_select_row)
        layout.addWidget(self.model_info_label)
        layout.addLayout(download_row)
        layout.addWidget(self.download_progress)
        layout.addWidget(separator)
        layout.addWidget(device_section)
        layout.addLayout(device_row)
        layout.addWidget(self.device_info_label)
        layout.addLayout(compute_row)
        layout.addSpacing(8)
        layout.addWidget(lang_section)
        layout.addLayout(lang_row)
        layout.addWidget(lang_info)
        
        return card
    
    def _test_microphone(self):
        """Test microphone by recording 3 seconds."""
        from PyQt5.QtCore import QTimer
        
        try:
            from scribe.core.audio_recorder import AudioRecorder
            
            # Get selected device
            device_id = self.device_combo.currentData()
            
            # Create recorder
            recorder = AudioRecorder()
            recorder.set_device(device_id)
            
            # Show info
            InfoBar.info(
                title="Testing Microphone",
                content="Recording for 3 seconds...",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            
            # Start recording
            recorder.start_recording()
            
            # Stop after 3 seconds
            def stop_test():
                audio_data = recorder.stop_recording()
                if audio_data:
                    InfoBar.success(
                        title="Test Successful",
                        content=f"Recorded {len(audio_data)} bytes",
                        orient=Qt.Orientation.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=2000,
                        parent=self
                    )
                else:
                    InfoBar.warning(
                        title="Test Warning",
                        content="No audio data captured",
                        orient=Qt.Orientation.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=2000,
                        parent=self
                    )
            
            QTimer.singleShot(3000, stop_test)
            
        except Exception as e:
            InfoBar.error(
                title="Test Failed",
                content=str(e),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
    
    def _create_appearance_settings(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Theme
        theme_row = QHBoxLayout()
        theme_label = BodyLabel("Theme")
        self.theme_combo = ComboBox()
        self.theme_combo.addItem("Auto", userData="auto")
        self.theme_combo.addItem("Light", userData="light")
        self.theme_combo.addItem("Dark", userData="dark")
        self.theme_combo.setFixedWidth(300)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_row.addWidget(theme_label)
        theme_row.addStretch()
        theme_row.addWidget(self.theme_combo)
        
        layout.addLayout(theme_row)
        
        return card
    
    def _create_logs_settings(self):
        """Create logs and debugging section."""
        from pathlib import Path
        
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Info text
        info_label = BodyLabel("View application logs for debugging and troubleshooting")
        info_label.setStyleSheet("color: #888;")
        layout.addWidget(info_label)
        
        # Log file path display - find most recent log
        log_dir = Path.home() / ".scribe" / "logs"
        try:
            log_files = sorted(log_dir.glob("scribe_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
            log_file = log_files[0] if log_files else log_dir / "scribe.log"
        except Exception:
            log_file = log_dir / "scribe.log"
        
        path_row = QHBoxLayout()
        path_label = BodyLabel("Current log:")
        path_value = BodyLabel(str(log_file.name))
        path_value.setStyleSheet("color: #4CAF50; font-family: monospace;")
        path_row.addWidget(path_label)
        path_row.addWidget(path_value, 1)
        layout.addLayout(path_row)
        
        # Buttons row
        buttons_row = QHBoxLayout()
        
        view_log_btn = PrimaryPushButton(FIF.DOCUMENT, "View Current Log")
        view_log_btn.setFixedWidth(160)
        view_log_btn.clicked.connect(self._view_log)
        
        open_folder_btn = PushButton(FIF.FOLDER, "Open Log Folder")
        open_folder_btn.setFixedWidth(160)
        open_folder_btn.clicked.connect(self._open_log_folder)
        
        clear_old_logs_btn = PushButton(FIF.DELETE, "Clear Old Logs")
        clear_old_logs_btn.setFixedWidth(150)
        clear_old_logs_btn.clicked.connect(self._clear_old_logs)
        
        buttons_row.addWidget(view_log_btn)
        buttons_row.addSpacing(8)
        buttons_row.addWidget(open_folder_btn)
        buttons_row.addSpacing(8)
        buttons_row.addWidget(clear_old_logs_btn)
        buttons_row.addStretch()
        
        layout.addLayout(buttons_row)
        
        return card
    
    def _view_log(self):
        """Open log viewer dialog."""
        from pathlib import Path
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
        from PyQt5.QtCore import Qt
        
        # Find most recent log file
        log_dir = Path.home() / ".scribe" / "logs"
        try:
            log_files = sorted(log_dir.glob("scribe_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
            log_file = log_files[0] if log_files else log_dir / "scribe.log"
        except Exception:
            log_file = log_dir / "scribe.log"
        
        # Check if log file exists
        if not log_file.exists():
            InfoBar.warning(
                title="No log file",
                content="Log file doesn't exist yet. Start using Scribe to generate logs.",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT
            )
            return
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Scribe Log Viewer - {log_file.name}")
        dialog.setMinimumSize(900, 600)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Text edit for log content
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                border: none;
                padding: 10px;
            }
        """)
        
        # Load log content (last 5000 lines to avoid memory issues)
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 5000 lines
                content = ''.join(lines[-5000:])
                text_edit.setPlainText(content)
                
                # Scroll to bottom
                text_edit.verticalScrollBar().setValue(
                    text_edit.verticalScrollBar().maximum()
                )
        except Exception as e:
            text_edit.setPlainText(f"Error reading log file: {e}")
        
        layout.addWidget(text_edit)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.exec_()
    
    def _open_log_folder(self):
        """Open the logs folder in file explorer."""
        from pathlib import Path
        import subprocess
        import sys
        
        log_dir = Path.home() / ".scribe" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', str(log_dir)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(log_dir)])
            else:
                subprocess.run(['xdg-open', str(log_dir)])
            
            InfoBar.success(
                title="Folder opened",
                content=f"Log folder: {log_dir}",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )
        except Exception as e:
            InfoBar.error(
                title="Error",
                content=f"Failed to open folder: {e}",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT
            )
    
    def _clear_old_logs(self):
        """Clear old log files, keeping only the most recent ones."""
        from pathlib import Path
        
        # Confirmation dialog
        result = MessageBox(
            "Clear Old Log Files?",
            "This will delete all log files except the 3 most recent. This action cannot be undone.",
            self
        ).exec_()
        
        if result != MessageBox.StandardButton.Yes:
            return
        
        log_dir = Path.home() / ".scribe" / "logs"
        
        try:
            # Get all log files sorted by modification time
            log_files = sorted(log_dir.glob("scribe_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Delete all except the 3 most recent
            deleted_count = 0
            for old_log in log_files[3:]:
                try:
                    old_log.unlink()
                    deleted_count += 1
                except Exception:
                    pass
            
            if deleted_count > 0:
                InfoBar.success(
                    title="Logs Cleaned",
                    content=f"Deleted {deleted_count} old log file{'s' if deleted_count != 1 else ''}",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.TOP_RIGHT
                )
            else:
                InfoBar.info(
                    title="No Old Logs",
                    content="Only recent log files found, nothing to delete",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.TOP_RIGHT
                )
        except Exception as e:
            InfoBar.error(
                title="Error",
                content=f"Failed to clear old logs: {e}",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT
            )
    
    def _load_from_config(self):
        """Load settings from ConfigManager into UI."""
        config = self.config_manager.config

        # Hotkey configuration
        try:
            activation_key = self.config_manager.get('recording_options', 'activation_key', default='ctrl+alt')
            # Convert meta to windows for display
            display_key = activation_key.replace('meta', 'windows')
            self.hotkey_button.setText(f"✓ {display_key.upper()}")
            self.hotkey_button.setStyleSheet("""
                PushButton {
                    font-size: 13px;
                    font-weight: bold;
                    background-color: #4CAF50;
                    border: 2px solid #66BB6A;
                    color: white;
                }
            """)
            self.current_hotkey_label.setText(f"Current: {display_key.upper()}")
            self._pending_hotkey = display_key
        except:
            self.hotkey_button.setText("✓ CTRL+ALT")
            self.current_hotkey_label.setText("Current: CTRL+ALT")
            self._pending_hotkey = "ctrl+alt"

        # UI settings
        self.minimize_tray_switch.setChecked(config.ui.minimize_to_tray)
        self.show_tray_switch.setChecked(config.ui.show_system_tray)
        self.start_minimized_switch.setChecked(config.ui.start_minimized)
        
        # Find and set theme
        theme_idx = self.theme_combo.findData(config.ui.theme)
        if theme_idx >= 0:
            self.theme_combo.setCurrentIndex(theme_idx)
        
        # Audio settings
        if config.audio.device_id is not None:
            device_idx = self.device_combo.findData(config.audio.device_id)
            if device_idx >= 0:
                self.device_combo.setCurrentIndex(device_idx)
        
        rate_idx = self.rate_combo.findData(config.audio.sample_rate)
        if rate_idx >= 0:
            self.rate_combo.setCurrentIndex(rate_idx)
        
        # Whisper settings
        model_idx = self.model_combo.findData(config.whisper.model)
        if model_idx >= 0:
            self.model_combo.setCurrentIndex(model_idx)
            self._on_model_changed()  # Update info display
        
        device_idx = self.compute_device_combo.findData(config.whisper.device)
        if device_idx >= 0:
            self.compute_device_combo.setCurrentIndex(device_idx)
            self._on_device_changed()  # Update device info
        
        compute_idx = self.compute_type_combo.findData(config.whisper.compute_type)
        if compute_idx >= 0:
            self.compute_type_combo.setCurrentIndex(compute_idx)
    
    def _on_model_changed(self):
        """Update model information display when model selection changes."""
        model = self.model_combo.currentData()
        if not model or model not in self.model_info:
            return
        
        info = self.model_info[model]
        
        # Detect if GPU is available to show appropriate timing
        device = self.compute_device_combo.currentData() if hasattr(self, 'compute_device_combo') else "cpu"
        has_gpu = False
        
        try:
            import torch
            has_gpu = torch.cuda.is_available()
        except:
            pass
        
        # Show relevant timing based on GPU availability
        if has_gpu and device in ["auto", "cuda"]:
            time_info = f"⏱️ <b>Time (GPU):</b> {info['time_gpu']} &nbsp; <span style='color: #888;'>CPU: {info['time_cpu']}</span>"
        else:
            time_info = f"⏱️ <b>Time (CPU):</b> {info['time_cpu']}" + (f" &nbsp; <span style='color: #888;'>GPU: {info['time_gpu']}</span>" if has_gpu else "")
        
        # Build info text with formatting
        info_text = f"""<b>📦 Size:</b> {info['size']} &nbsp;&nbsp; <b>⚡ Speed:</b> {info['speed']} &nbsp;&nbsp; <b>✨ Quality:</b> {info['quality']}
<br>{time_info}
<br><br><b style="color: #4CAF50;">✅ Pros:</b> {info['pros']}
<br><b style="color: #F44336;">❌ Cons:</b> {info['cons']}
<br><br><b>🎯 Best For:</b> {info['best_for']}"""
        
        self.model_info_label.setText(info_text)
        
        # Check if model is downloaded
        self._check_model_downloaded(model)
    
    def _check_model_downloaded(self, model):
        """Check if model is already downloaded and show/hide download button."""
        import os
        from pathlib import Path
        
        # Check in models directory
        model_dir = Path("models") / f"models--Systran--faster-whisper-{model}"
        
        if model_dir.exists() and any(model_dir.iterdir()):
            self.download_model_btn.setVisible(False)
            self.download_model_btn.setText("✅ Model Downloaded")
        else:
            self.download_model_btn.setVisible(True)
            self.download_model_btn.setText(f"📥 Download {model.title()} Model")
    
    def _on_device_changed(self):
        """Update device information when compute device changes."""
        device = self.compute_device_combo.currentData()
        
        device_info = {
            "auto": "🤖 Automatically selects best available device (CPU/GPU)",
            "cpu": "💻 Uses CPU - Works everywhere, slower for large models",
            "cuda": "🚀 Uses NVIDIA GPU - 2-3x faster! Requires CUDA toolkit installed"
        }
        
        info_text = device_info.get(device, "")
        self.device_info_label.setText(info_text)
        
        # Recommend compute type based on device
        if device == "cuda":
            # GPU: recommend float16
            compute_idx = self.compute_type_combo.findData("float16")
            if compute_idx >= 0:
                self.compute_type_combo.setCurrentIndex(compute_idx)
        elif device == "cpu":
            # CPU: recommend int8
            compute_idx = self.compute_type_combo.findData("int8")
            if compute_idx >= 0:
                self.compute_type_combo.setCurrentIndex(compute_idx)
    
    def _on_language_changed(self):
        """Update language setting when user changes selection."""
        lang_code = self.language_combo.currentData()
        
        # Update config and auto-save
        if self.config_manager:
            try:
                config = self.config_manager.config
                # Update whisper config with language
                self.config_manager.set('whisper', 'language', lang_code if lang_code != "auto" else None)
                
                # Auto-save like modern apps
                saved_path = self.config_manager.save()
                logger.info(f"Language changed to: {lang_code}, auto-saved to {saved_path}")
                
                # Show brief confirmation
                InfoBar.success(
                    title="Language Updated",
                    content=f"Language set to {lang_code or 'auto-detect'}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=1500,
                    parent=self
                )
                
                # Language change doesn't require model reload - just config update
                # Don't emit config_changed signal for language
                
            except Exception as e:
                logger.error(f"Failed to save language setting: {e}", exc_info=True)
                InfoBar.error(
                    title="Save Failed",
                    content=f"Failed to save language setting: {str(e)}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=3000,
                    parent=self
                )
    
    def _download_model(self):
        """Download the selected Whisper model."""
        model = self.model_combo.currentData()
        
        # Show confirmation dialog
        title = f"Download {model.title()} Model?"
        info = self.model_info[model]
        content = f"""This will download the {model} model ({info['size']}).

Quality: {info['quality']}
Speed: {info['speed']}

Continue?"""
        
        w = MessageBox(title, content, self)
        if w.exec():
            self._start_model_download(model)
    
    def _start_model_download(self, model):
        """Start downloading model in background thread."""
        self.download_model_btn.setEnabled(False)
        self.download_model_btn.setText("⏳ Downloading...")
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        
        # Create worker thread
        from PyQt5.QtCore import QThread, pyqtSignal
        
        class ModelDownloader(QThread):
            progress = pyqtSignal(int, str)
            finished = pyqtSignal(bool, str)
            
            def __init__(self, model_name):
                super().__init__()
                self.model_name = model_name
            
            def run(self):
                try:
                    from faster_whisper import WhisperModel
                    
                    self.progress.emit(10, "Connecting to HuggingFace...")
                    
                    # This will download the model if not present
                    model = WhisperModel(
                        self.model_name,
                        device="cpu",
                        compute_type="int8",
                        download_root="models"
                    )
                    
                    self.progress.emit(100, "Download complete!")
                    self.finished.emit(True, f"Model {self.model_name} downloaded successfully!")
                    
                except Exception as e:
                    self.finished.emit(False, f"Download failed: {str(e)}")
        
        self.downloader = ModelDownloader(model)
        self.downloader.progress.connect(self._on_download_progress)
        self.downloader.finished.connect(self._on_download_finished)
        self.downloader.start()
    
    def _on_download_progress(self, value, message):
        """Update download progress."""
        self.download_progress.setValue(value)
        self.download_model_btn.setText(f"⏳ {message}")
    
    def _on_download_finished(self, success, message):
        """Handle download completion."""
        self.download_progress.setVisible(False)
        self.download_model_btn.setEnabled(True)
        
        if success:
            InfoBar.success(
                title="Download Complete",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            # Update button state
            self._check_model_downloaded(self.model_combo.currentData())
        else:
            InfoBar.error(
                title="Download Failed",
                content=message,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
            self.download_model_btn.setText("🔄 Retry Download")
    
    def _save_config(self):
        """Save UI settings to ConfigManager."""
        try:
            # Hotkey setting - use pending hotkey if set, otherwise extract from button
            if hasattr(self, '_pending_hotkey') and self._pending_hotkey:
                hotkey_text = self._pending_hotkey
            else:
                # Extract from button text (e.g., "✓ CTRL+ALT" -> "ctrl+alt")
                button_text = self.hotkey_button.text()
                hotkey_text = button_text.replace('✓ ', '').replace('⌨️ ', '').lower().strip()
            
            if hotkey_text:
                # Convert windows to meta for storage
                storage_key = hotkey_text.replace('windows', 'meta')
                self.config_manager.set('hotkey', 'activation_key', storage_key)

            # UI settings
            self.config_manager.set('ui', 'minimize_to_tray', self.minimize_tray_switch.isChecked())
            self.config_manager.set('ui', 'show_system_tray', self.show_tray_switch.isChecked())
            self.config_manager.set('ui', 'start_minimized', self.start_minimized_switch.isChecked())
            self.config_manager.set('ui', 'theme', self.theme_combo.currentData())
            
            # Audio settings
            device_id = self.device_combo.currentData()
            self.config_manager.set('audio', 'device_id', device_id)
            self.config_manager.set('audio', 'sample_rate', self.rate_combo.currentData())
            
            # Whisper settings
            self.config_manager.set('whisper', 'model', self.model_combo.currentData())
            self.config_manager.set('whisper', 'device', self.compute_device_combo.currentData())
            self.config_manager.set('whisper', 'compute_type', self.compute_type_combo.currentData())
            
            # Language setting (if user changed it)
            lang_code = self.language_combo.currentData()
            if lang_code:
                self.config_manager.set('whisper', 'language', lang_code if lang_code != "auto" else None)
            
            # Save to file
            saved_path = self.config_manager.save()
            logger.info(f"Configuration saved successfully to {saved_path}")
            
            InfoBar.success(
                title="Settings Saved",
                content=f"Configuration saved to {saved_path.name}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            
            self.config_changed.emit("all")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}", exc_info=True)
            InfoBar.error(
                title="Save Failed",
                content=str(e),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
    
    def _connect_auto_save_handlers(self):
        """Connect all controls to auto-save their changes."""
        # UI switches
        self.minimize_tray_switch.checkedChanged.connect(self._auto_save_ui_setting)
        self.show_tray_switch.checkedChanged.connect(self._auto_save_ui_setting)
        self.start_minimized_switch.checkedChanged.connect(self._auto_save_ui_setting)
        
        # Audio settings
        self.device_combo.currentIndexChanged.connect(self._auto_save_audio_setting)
        self.rate_combo.currentIndexChanged.connect(self._auto_save_audio_setting)
        
        # Whisper settings
        self.model_combo.currentIndexChanged.connect(self._auto_save_whisper_setting)
        self.compute_device_combo.currentIndexChanged.connect(self._auto_save_whisper_setting)
        self.compute_type_combo.currentIndexChanged.connect(self._auto_save_whisper_setting)
    
    def _auto_save_ui_setting(self):
        """Auto-save UI settings when changed."""
        try:
            self.config_manager.set('ui', 'minimize_to_tray', self.minimize_tray_switch.isChecked())
            self.config_manager.set('ui', 'show_system_tray', self.show_tray_switch.isChecked())
            self.config_manager.set('ui', 'start_minimized', self.start_minimized_switch.isChecked())
            self.config_manager.save()
            logger.info("UI settings auto-saved")
        except Exception as e:
            logger.error(f"Failed to auto-save UI setting: {e}", exc_info=True)
    
    def _auto_save_audio_setting(self):
        """Auto-save audio settings when changed."""
        try:
            device_id = self.device_combo.currentData()
            self.config_manager.set('audio', 'device_id', device_id)
            self.config_manager.set('audio', 'sample_rate', self.rate_combo.currentData())
            self.config_manager.save()
            logger.info("Audio settings auto-saved")
        except Exception as e:
            logger.error(f"Failed to auto-save audio setting: {e}", exc_info=True)
    
    def _auto_save_whisper_setting(self):
        """Auto-save Whisper settings when changed."""
        try:
            self.config_manager.set('whisper', 'model', self.model_combo.currentData())
            self.config_manager.set('whisper', 'device', self.compute_device_combo.currentData())
            self.config_manager.set('whisper', 'compute_type', self.compute_type_combo.currentData())
            self.config_manager.save()
            logger.info("Whisper settings auto-saved")
            
            # Reload transcription engine with new settings
            self.config_changed.emit("whisper")
        except Exception as e:
            logger.error(f"Failed to auto-save Whisper setting: {e}", exc_info=True)
    
    def _on_theme_changed(self, theme_name: str):
        """Apply theme change immediately and save."""
        theme_map = {"Auto": Theme.AUTO, "Light": Theme.LIGHT, "Dark": Theme.DARK}
        setTheme(theme_map.get(theme_name, Theme.AUTO))
        
        # Auto-save theme preference
        try:
            theme_key = theme_name.lower()
            self.config_manager.set('ui', 'theme', theme_key)
            self.config_manager.save()
            logger.info(f"Theme changed to: {theme_name}, auto-saved")
        except Exception as e:
            logger.error(f"Failed to save theme setting: {e}", exc_info=True)
    
    def _on_accent_changed(self, color_name: str):
        """Apply accent color change immediately."""
        color_map = {
            "Purple (Scribe)": "#6751A1",
            "Blue": "#4A90E2",
            "Green": "#52C41A",
            "Orange": "#FA8C16"
        }
        setThemeColor(color_map.get(color_name, "#6751A1"))
    
    def _capture_hotkey(self):
        """Capture hotkey by listening for key press."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
        from PyQt5.QtCore import QTimer, Qt
        
        # Create modal dialog for key capture
        dialog = QDialog(self)
        dialog.setWindowTitle("Capture Hotkey")
        dialog.setModal(True)
        dialog.setFixedSize(400, 200)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        
        instruction = QLabel("⌨️ Press your desired key combination now...")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet("font-size: 16px; color: #FF9800; font-weight: bold;")
        
        status_label = QLabel("Waiting...")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("font-size: 14px; color: #888;")
        
        layout.addStretch()
        layout.addWidget(instruction)
        layout.addWidget(status_label)
        layout.addStretch()
        
        # Store references for event filter
        dialog._status_label = status_label
        dialog._captured = False
        dialog._captured_hotkey = None
        
        # Install event filter on dialog
        def capture_event(obj, event):
            if event.type() == QEvent.KeyPress and not dialog._captured:
                # Get modifiers
                modifiers = event.modifiers()
                keys = []
                
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    keys.append('ctrl')
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    keys.append('shift')
                if modifiers & Qt.KeyboardModifier.AltModifier:
                    keys.append('alt')
                if modifiers & Qt.KeyboardModifier.MetaModifier:
                    keys.append('windows')
                
                # Add the actual key if it's not a modifier
                key = event.key()
                if key not in [Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta]:
                    key_text = event.text().lower()
                    if key_text and key_text.isalnum():
                        keys.append(key_text)
                    elif key in [Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter]:
                        key_names = {Qt.Key_Space: 'space', Qt.Key_Return: 'enter', Qt.Key_Enter: 'enter'}
                        keys.append(key_names.get(key, 'unknown'))
                
                # If we have at least 2 keys (modifier + key), capture it
                if len(keys) >= 2:
                    hotkey_str = '+'.join(keys)
                    dialog._captured_hotkey = hotkey_str
                    dialog._captured = True
                    status_label.setText(f"✓ Captured: {hotkey_str.upper()}")
                    status_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")
                    QTimer.singleShot(500, dialog.accept)
                    return True
                elif len(keys) == 1:
                    status_label.setText(f"Press a modifier + key (not just '{keys[0]}')")
                    status_label.setStyleSheet("font-size: 14px; color: #FF9800;")
            
            return False
        
        dialog.eventFilter = capture_event
        dialog.installEventFilter(dialog)
        
        # Auto-close after 5 seconds
        QTimer.singleShot(5000, lambda: dialog.reject() if not dialog._captured else None)
        
        # Show dialog
        result = dialog.exec_()
        
        if result == QDialog.DialogCode.Accepted and dialog._captured_hotkey:
            self._finish_capture(dialog._captured_hotkey)
        else:
            self.hotkey_button.setText("⏱️ Cancelled")
            QTimer.singleShot(1000, lambda: self.hotkey_button.setText("Click to Set Hotkey"))
    
    def _finish_capture(self, hotkey: str):
        """Finish hotkey capture with the given hotkey string."""
        # Update button and current hotkey label
        self.hotkey_button.setText(f"✓ {hotkey.upper()}")
        self.hotkey_button.setStyleSheet("""
            PushButton {
                font-size: 12px;
                font-weight: bold;
                background-color: #4CAF50;
                border: 2px solid #66BB6A;
                color: white;
            }
            PushButton:hover {
                background-color: #66BB6A;
            }
        """)
        
        self.current_hotkey_label.setText(f"Current: {hotkey.upper()}")
        
        # Store in a temporary variable (will be saved when user clicks Save)
        self._pending_hotkey = hotkey
    
    def _reset_hotkey(self):
        """Reset hotkey to default (Ctrl+Alt)."""
        default_hotkey = "ctrl+alt"
        self.hotkey_button.setText(f"✓ {default_hotkey.upper()}")
        self.hotkey_button.setStyleSheet("""
            PushButton {
                font-size: 13px;
                font-weight: bold;
                background-color: #4CAF50;
                border: 2px solid #66BB6A;
                color: white;
            }
        """)
        self.current_hotkey_label.setText(f"Current: {default_hotkey.upper()}")
        self._pending_hotkey = default_hotkey

