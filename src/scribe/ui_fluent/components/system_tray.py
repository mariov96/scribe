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
    start_recording_clicked = Signal()
    stop_recording_clicked = Signal()
    settings_clicked = Signal()
    quit_clicked = Signal()

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
        self.show_action = QAction("Show Window", menu)
        self.show_action.triggered.connect(self.show_window_clicked.emit)
        menu.addAction(self.show_action)

        # Start/Stop Recording (dynamic)
        self.record_action = QAction("Start Recording", menu)
        self.record_action.triggered.connect(self._toggle_recording)
        menu.addAction(self.record_action)

        menu.addSeparator()

        # === NAVIGATION ===
        settings_action = QAction("Settings", menu)
        settings_action.triggered.connect(self.settings_clicked.emit)
        menu.addAction(settings_action)

        insights_action = QAction("View Insights", menu)
        # TODO: Connect to insights page signal
        menu.addAction(insights_action)

        history_action = QAction("View History", menu)
        # TODO: Connect to history page signal
        menu.addAction(history_action)

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

    def _on_activated(self, reason):
        """Handle tray icon activation (click, double-click)."""
        if reason == QSystemTrayIcon.DoubleClick:
            # Double-click shows main window
            self.show_window_clicked.emit()
        elif reason == QSystemTrayIcon.Trigger:
            # Single left-click also shows window (Windows behavior)
            self.show_window_clicked.emit()

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
