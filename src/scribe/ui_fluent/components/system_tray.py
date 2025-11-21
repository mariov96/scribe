"""
Modern System Tray Implementation
Clean, comprehensive menu with status indicators and quick actions.
"""

import logging
from pathlib import Path
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal as Signal

logger = logging.getLogger(__name__)


class ScribeSystemTray(QSystemTrayIcon):
    """
    Modern system tray with comprehensive menu and status indicators.
    """

    # Signals
    show_window_clicked = Signal()
    toggle_visibility_clicked = Signal()
    start_recording_clicked = Signal()
    stop_recording_clicked = Signal()
    settings_clicked = Signal()
    history_clicked = Signal()
    insights_clicked = Signal()
    about_clicked = Signal()
    quit_clicked = Signal()
    microphone_selected = Signal(object)  # Optional[int]
    microphone_next_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._recording = False
        self._setup_tray()

    def _setup_tray(self):
        """Initialize modern system tray with comprehensive menu."""
        try:
            # Set custom Scribe icon
            icon_path = Path(__file__).parent.parent.parent.parent / "assets" / "scribe-icon.ico"
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                self.setIcon(icon)
                logger.info(f"Loaded custom tray icon from {icon_path}")
            else:
                # Fallback to theme icon
                icon = QIcon.fromTheme("audio-input-microphone")
                self.setIcon(icon)
                logger.warning(f"Custom icon not found at {icon_path}, using fallback")

            # Set tooltip
            self.setToolTip("Scribe - Voice Control for Your Workflow")

            # Create comprehensive menu
            self._create_menu()

            # Connect double-click to show window
            self.activated.connect(self._on_activated)

            # Try to show tray icon
            self._show_with_fallback()

        except Exception as e:
            logger.error(f"Failed to setup system tray: {e}", exc_info=True)
            self._setup_fallback()

    def _create_menu(self):
        """Create modern, comprehensive context menu."""
        menu = QMenu()

        # Apply modern styling
        menu.setStyleSheet("""
            QMenu {
                background-color: #2D2D2D;
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px 8px 12px;
                border-radius: 4px;
                color: #E8E8E8;
            }
            QMenu::item:selected {
                background-color: #6751A1;
            }
            QMenu::item:disabled {
                color: #707070;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3A3A3A;
                margin: 4px 8px;
            }
        """)

        # === HEADER ===
        header_action = QAction("Scribe v2.0", menu)
        header_action.setEnabled(False)
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(10)
        header_action.setFont(header_font)
        menu.addAction(header_action)

        menu.addSeparator()

        # === QUICK ACTIONS ===
        # Show/Hide Window
        self.show_hide_action = QAction("Show Scribe", menu)
        self.show_hide_action.triggered.connect(self.toggle_visibility_clicked.emit)
        menu.addAction(self.show_hide_action)

        menu.addSeparator()

        # Microphone submenu
        self.mic_menu = QMenu("Microphone", menu)
        self._populate_mic_menu(self.mic_menu)
        menu.addMenu(self.mic_menu)

        # Quick: Next Mic
        next_mic_action = QAction("Next Microphone", menu)
        next_mic_action.triggered.connect(self.microphone_next_requested.emit)
        menu.addAction(next_mic_action)

        # Start/Stop Recording (dynamic)
        self.record_action = QAction("Start Recording", menu)
        self.record_action.triggered.connect(self._toggle_recording)
        menu.addAction(self.record_action)

        menu.addSeparator()

        # === NAVIGATION ===
        settings_action = QAction("Settings", menu)
        settings_action.triggered.connect(self.settings_clicked.emit)
        menu.addAction(settings_action)

        history_action = QAction("History", menu)
        history_action.triggered.connect(self.history_clicked.emit)
        menu.addAction(history_action)

        insights_action = QAction("Insights", menu)
        insights_action.triggered.connect(self.insights_clicked.emit)
        menu.addAction(insights_action)

        about_action = QAction("About Scribe", menu)
        about_action.triggered.connect(self.about_clicked.emit)
        menu.addAction(about_action)

        menu.addSeparator()

        # === STATUS INFO ===
        # Recording status indicator
        self.status_action = QAction("Status: Ready", menu)
        self.status_action.setEnabled(False)
        status_font = QFont()
        status_font.setPointSize(9)
        self.status_action.setFont(status_font)
        menu.addAction(self.status_action)

        menu.addSeparator()

        # === EXIT ===
        quit_action = QAction("Quit Scribe", menu)
        quit_action.triggered.connect(self.quit_clicked.emit)
        quit_font = QFont()
        quit_font.setPointSize(10)
        quit_action.setFont(quit_font)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _populate_mic_menu(self, menu: QMenu):
        """Populate microphone submenu with valid input devices as radio actions."""
        try:
            menu.clear()
            # Import here to avoid circular imports or early initialization issues
            from scribe.core.audio_recorder import AudioRecorder
            devices = AudioRecorder.list_valid_input_devices(sample_rate=16000)
            
            # System default option
            default_act = QAction("System Default", menu)
            default_act.setCheckable(True)
            default_act.triggered.connect(lambda: self.microphone_selected.emit(None))
            menu.addAction(default_act)
            
            if devices:
                menu.addSeparator()
                
            for d in devices:
                label = f"{d['name']}" + ("  (Default)" if d.get('is_default') else "")
                act = QAction(label, menu)
                act.setCheckable(True)
                act.triggered.connect(lambda checked, dev_id=d['id']: self.microphone_selected.emit(dev_id))
                menu.addAction(act)
        except Exception as e:
            logger.error(f"Failed to populate mic menu: {e}")

    def _toggle_recording(self):
        """Toggle recording state and emit appropriate signal."""
        if self._recording:
            self.stop_recording_clicked.emit()
        else:
            self.start_recording_clicked.emit()

    def update_recording_state(self, recording: bool):
        """
        Update tray menu to reflect current recording state.

        Args:
            recording: True if currently recording, False otherwise
        """
        self._recording = recording

        if recording:
            self.record_action.setText("Stop Recording")
            self.status_action.setText("Status: Recording...")
            self.setToolTip("Scribe - Recording...")
        else:
            self.record_action.setText("Start Recording")
            self.status_action.setText("Status: Ready")
            self.setToolTip("Scribe - Voice Control for Your Workflow")

    def update_visibility_text(self, is_visible: bool):
        """Update the Show/Hide menu item text."""
        if is_visible:
            self.show_hide_action.setText("Hide Scribe")
        else:
            self.show_hide_action.setText("Show Scribe")

    def _on_activated(self, reason):
        """Handle tray icon activation (click, double-click)."""
        if reason == QSystemTrayIcon.DoubleClick:
            # Double-click toggles visibility
            self.toggle_visibility_clicked.emit()
        elif reason == QSystemTrayIcon.Trigger:
            # Single left-click also toggles visibility (Windows behavior)
            self.toggle_visibility_clicked.emit()

    def show_notification(self, title: str, message: str, duration: int = 3000):
        """
        Show system tray notification.

        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds (default: 3000)
        """
        try:
            self.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                duration
            )
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")

    def _show_with_fallback(self):
        """Attempt to show tray icon with fallback."""
        try:
            # First try standard tray
            if self.isSystemTrayAvailable():
                self.show()
                logger.info("System tray icon displayed successfully")
                return True

            # Check if we're in WSL
            import os
            if 'WSL_DISTRO_NAME' in os.environ:
                logger.info("WSL environment detected, attempting notification daemon")
                # Try XDG notification daemon
                import subprocess
                subprocess.run(
                    ['notify-send', 'Scribe', 'Running in system tray'],
                    check=False,
                    timeout=2
                )
                self.show()
                return True

            logger.warning("System tray not available on this platform")
            return False

        except Exception as e:
            logger.error(f"Error showing tray icon: {e}", exc_info=True)
            return False

    def _setup_fallback(self):
        """Setup minimal fallback tray support."""
        try:
            logger.info("Setting up fallback system tray")
            # Create minimal menu
            menu = QMenu()

            show_action = QAction("Show Scribe", menu)
            show_action.triggered.connect(self.show_window_clicked.emit)
            menu.addAction(show_action)

            menu.addSeparator()

            quit_action = QAction("Quit", menu)
            quit_action.triggered.connect(self.quit_clicked.emit)
            menu.addAction(quit_action)

            self.setContextMenu(menu)

            # Try to show
            self.show()
            logger.info("Fallback tray setup complete")

        except Exception as e:
            logger.error(f"Failed to setup fallback tray: {e}", exc_info=True)
