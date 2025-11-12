"""
Scribe Main Window
MSFluentWindow with navigation, system tray, and all pages
"""

import sys
import logging
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal as Signal
from PyQt5.QtWidgets import QAction, QGraphicsOpacityEffect
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QCursor
from qfluentwidgets import (
    MSFluentWindow, NavigationItemPosition, FluentIcon as FIF,
    setTheme, Theme, setThemeColor, InfoBar, InfoBarPosition
)

from .branding import SCRIBE_VERSION, SCRIBE_TAGLINE, SCRIBE_PURPLE, UI_SCALE_FACTOR, DEFAULT_FONT_SIZE
from .pages import (
    HomePage, PluginsPage, InsightsPage, 
    SettingsPage, AboutPage, HistoryPage
)
from scribe.config import ConfigManager

logger = logging.getLogger(__name__)


class ScribeMainWindow(MSFluentWindow):
    """Main window with branding and system tray"""
    
    # Signals for app integration
    start_listening_requested = Signal()
    stop_listening_requested = Signal()
    test_audio_requested = Signal()
    settings_requested = Signal()
    
    def __init__(self, config_manager: ConfigManager = None, plugin_registry=None, value_calculator=None):
        super().__init__()
        
        self.config_manager = config_manager or ConfigManager()
        self.plugin_registry = plugin_registry
        self.value_calculator = value_calculator
        
        # Page transition animation setup
        self._setup_page_animations()
        
        # Force dark theme for better readability
        setTheme(Theme.DARK)
        setThemeColor(SCRIBE_PURPLE)

        # Set dark palette for better contrast
        from PyQt5.QtGui import QPalette, QColor
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(37, 37, 37))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ToolTipText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Link, QColor(103, 81, 161))
        dark_palette.setColor(QPalette.Highlight, QColor(103, 81, 161))
        dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        QApplication.instance().setPalette(dark_palette)

        self.setWindowTitle(f"Scribe - {SCRIBE_TAGLINE}")
        
        # Get the screen where the cursor is (active monitor in multi-monitor setup)
        cursor_pos = QCursor.pos()
        active_screen = QApplication.screenAt(cursor_pos)
        if not active_screen:
            active_screen = QApplication.primaryScreen()
        
        screen_geometry = active_screen.availableGeometry()
        
        # Get DPI scaling factor
        dpi_ratio = active_screen.devicePixelRatio()
        
        # Physical screen size (actual pixels / DPI ratio)
        physical_width = screen_geometry.width() / dpi_ratio
        physical_height = screen_geometry.height() / dpi_ratio
        
        logger.info(f"Active screen: {screen_geometry.width()}x{screen_geometry.height()} @ {dpi_ratio}x DPI")
        logger.info(f"Physical size: {physical_width:.0f}x{physical_height:.0f}")
        
        # Target 60% of physical screen size
        target_width = int(physical_width * 0.60)
        target_height = int(physical_height * 0.60)
        
        # Apply DPI scaling back for Qt logical pixels
        window_width = int(target_width * dpi_ratio)
        window_height = int(target_height * dpi_ratio)
        
        logger.info(f"Setting window size: {window_width}x{window_height}")
        
        self.resize(window_width, window_height)
        self.setMinimumSize(700, 480)

        # Center window on the active screen
        frame_geometry = self.frameGeometry()
        screen_center = screen_geometry.center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
        
        logger.info(f"Window centered at: {frame_geometry.topLeft()}")
        
        # Set window icon
        self._set_window_icon()
        
        self._setup_system_tray()
        self._create_pages()
        self._add_navigation()
        
        # Create recording widget
        from .widgets import RecordingWidget
        self.recording_widget = RecordingWidget(self)
        self.recording_widget.hide()

        # Apply darker background for better contrast with white text
        # Using !important to override qfluentwidgets defaults
        dark_background_style = """
        /* Main window background - very dark */
        QMainWindow, MSFluentWindow {
            background-color: #1E1E1E !important;
        }

        /* Content area - dark gray */
        QScrollArea, ScrollArea {
            background-color: #252525 !important;
            border: none !important;
        }

        /* Viewport (content inside scroll areas) */
        QScrollArea > QWidget, ScrollArea > QWidget {
            background-color: #252525 !important;
        }

        /* Cards - slightly lighter for contrast */
        CardWidget {
            background-color: #2D2D2D !important;
            border: 1px solid #3F3F3F !important;
        }

        /* All labels should be light colored */
        QLabel, TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel, StrongBodyLabel {
            color: #F0F0F0 !important;
        }

        /* Navigation sidebar - darkest */
        NavigationInterface, QWidget#navigationWidget {
            background-color: #1A1A1A !important;
        }
        
        /* Button hover effects */
        PrimaryPushButton:hover {
            background-color: #7E57C2 !important;
        }
        
        PushButton:hover {
            background-color: #3A3A3A !important;
        }
        
        /* Smooth transitions */
        PrimaryPushButton, PushButton, CardWidget {
            transition: all 0.2s ease-in-out;
        }
        """
        self.setStyleSheet(dark_background_style)

        QTimer.singleShot(500, self._show_welcome)
    
    def _setup_page_animations(self):
        """Setup fade animations for page transitions"""
        # We'll add opacity effects to pages after they're created
        self._page_opacity_effects = {}
        self._page_animations = {}
    
    def _add_page_animation(self, page):
        """Add fade animation to a page"""
        opacity_effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(opacity_effect)
        
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(250)  # 250ms fade
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self._page_opacity_effects[page] = opacity_effect
        self._page_animations[page] = animation
    
    def switchTo(self, widget):
        """Override to add fade animation when switching pages"""
        # Stop and finish all running animations to prevent concurrent painting
        for page, anim in self._page_animations.items():
            if anim.state() == QPropertyAnimation.Running:
                anim.stop()
                # Set opacity to final value immediately
                effect = self._page_opacity_effects.get(page)
                if effect:
                    if page == self.stackedWidget.currentWidget():
                        effect.setOpacity(0.0)  # Fade out current
                    else:
                        effect.setOpacity(1.0)  # Reset others
        
        # Fade out current page
        current = self.stackedWidget.currentWidget()
        if current and current in self._page_animations:
            current_anim = self._page_animations[current]
            current_anim.setStartValue(1.0)
            current_anim.setEndValue(0.0)
            current_anim.start()
        
        # Switch page
        super().switchTo(widget)
        
        # Fade in new page
        if widget in self._page_animations:
            new_anim = self._page_animations[widget]
            new_anim.setStartValue(0.0)
            new_anim.setEndValue(1.0)
            new_anim.start()
    
    def _set_window_icon(self):
        """Set window and app icon"""
        from pathlib import Path
        from PyQt5.QtGui import QIcon
        
        # Find assets directory (works from any working directory)
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        assets_dir = project_root / 'assets'
        
        # Try .ico first (Windows), then .png
        icon_path = assets_dir / 'scribe-icon.ico'
        if not icon_path.exists():
            icon_path = assets_dir / 'scribe-icon.png'
        
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.setWindowIcon(icon)
            # Also set for QApplication
            QApplication.instance().setWindowIcon(icon)
    
    def _setup_system_tray(self):
        """Create system tray icon with styled menu"""
        from PyQt5.QtGui import QFont, QColor, QPalette
        
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use window icon for tray (already loaded in _set_window_icon)
        icon = self.windowIcon()
        if not icon.isNull():
            self.tray_icon.setIcon(icon)
        
        self.tray_icon.setToolTip(f"Scribe {SCRIBE_VERSION} - Voice to Text")
        
        # Create styled tray menu
        tray_menu = QMenu()
        
        # Apply dark theme styling to menu
        menu_style = """
        QMenu {
            background-color: #2D2D2D;
            color: #F0F0F0;
            border: 1px solid #404040;
            border-radius: 8px;
            padding: 8px 0px;
            font-size: 13px;
        }
        QMenu::item {
            padding: 8px 32px 8px 16px;
            background-color: transparent;
        }
        QMenu::item:selected {
            background-color: #6751A1;
            color: #FFFFFF;
        }
        QMenu::separator {
            height: 1px;
            background: #404040;
            margin: 6px 8px;
        }
        QMenu::icon {
            padding-left: 8px;
        }
        """
        tray_menu.setStyleSheet(menu_style)
        
        # Set menu font
        menu_font = QFont("Segoe UI", 10)
        tray_menu.setFont(menu_font)
        
        # Show/Hide action with icon
        self.show_hide_action = QAction("  Show Scribe", self)
        self.show_hide_action.triggered.connect(self._toggle_show_hide)
        tray_menu.addAction(self.show_hide_action)
        
        tray_menu.addSeparator()
        
        # Start Listening action
        start_action = QAction("  🎤  Start Listening", self)
        start_action.triggered.connect(self._on_tray_start_listening)
        tray_menu.addAction(start_action)
        
        tray_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("  ⚙️  Settings", self)
        settings_action.triggered.connect(self._on_tray_settings)
        tray_menu.addAction(settings_action)
        
        # History action
        history_action = QAction("  📜  History", self)
        history_action.triggered.connect(self._on_tray_history)
        tray_menu.addAction(history_action)
        
        # About action
        about_action = QAction("  ℹ️  About Scribe", self)
        about_action.triggered.connect(self._on_tray_about)
        tray_menu.addAction(about_action)
        
        tray_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("  ❌  Quit Scribe", self)
        quit_action.triggered.connect(self._quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Double-click to show window
        self.tray_icon.activated.connect(self._on_tray_activated)
    
    def _toggle_show_hide(self):
        """Toggle window visibility"""
        if self.isVisible():
            self.hide()
            self.show_hide_action.setText("  Show Scribe")
        else:
            self.show()
            self.activateWindow()
            self.show_hide_action.setText("  Hide Scribe")
    
    def _quit_application(self):
        """Actually quit the application"""
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        QApplication.quit()
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()
            self.show_hide_action.setText("  Hide Scribe")
    
    def _on_tray_start_listening(self):
        """Start listening from tray"""
        self.show()
        self.activateWindow()
        self.show_hide_action.setText("  Hide Scribe")
        # Navigate to insights page
        self.stackedWidget.setCurrentWidget(self.insights_page)
    
    def _on_tray_settings(self):
        """Open settings from tray"""
        self.show()
        self.activateWindow()
        self.show_hide_action.setText("  Hide Scribe")
        self.stackedWidget.setCurrentWidget(self.settings_page)
    
    def _on_tray_history(self):
        """Open history from tray"""
        self.show()
        self.activateWindow()
        self.show_hide_action.setText("  Hide Scribe")
        self.stackedWidget.setCurrentWidget(self.history_page)
    
    def _on_tray_about(self):
        """Open about from tray"""
        self.show()
        self.activateWindow()
        self.show_hide_action.setText("  Hide Scribe")
        self.stackedWidget.setCurrentWidget(self.about_page)
    
    def _create_pages(self):
        self.home_page = HomePage(self.value_calculator, self)
        self.insights_page = InsightsPage(self.value_calculator, self)
        self.history_page = HistoryPage(self)
        self.plugins_page = PluginsPage(self.plugin_registry, self.config_manager, self)
        self.settings_page = SettingsPage(self.config_manager, self)
        self.about_page = AboutPage(self)
        
        # Add fade animations to all pages
        for page in [self.home_page, self.insights_page, self.history_page, 
                     self.plugins_page, self.settings_page, self.about_page]:
            self._add_page_animation(page)

        # Connect home page signals
        self.home_page.start_listening_clicked.connect(self.start_listening_requested.emit)
        self.home_page.test_audio_clicked.connect(self._on_test_audio)
        self.home_page.settings_clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.settings_page))
    
    def _add_navigation(self):
        self.addSubInterface(self.home_page, FIF.HOME, "Home")
        self.addSubInterface(self.insights_page, FIF.PIE_SINGLE, "Insights")
        self.addSubInterface(self.history_page, FIF.HISTORY, "History")
        self.addSubInterface(self.plugins_page, FIF.GAME, "Plugins")
        
        # Bottom navigation
        self.addSubInterface(
            self.settings_page,
            FIF.SETTING,
            "Settings",
            position=NavigationItemPosition.BOTTOM
        )
        
        self.addSubInterface(
            self.about_page,
            FIF.INFO,
            "About",
            position=NavigationItemPosition.BOTTOM
        )
    
    def _show_welcome(self):
        InfoBar.success(
            title="Welcome to Scribe!",
            content=SCRIBE_TAGLINE,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self
        )
    
    def closeEvent(self, event):
        """Minimize to tray on close button, hold Shift to actually quit"""
        from PyQt5.QtWidgets import QMessageBox
        from PyQt5.QtCore import Qt as QtCore
        
        # Check if Shift key is held
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.ShiftModifier:
            # Shift held - actually quit
            reply = QMessageBox.question(
                self, 
                'Quit Scribe?',
                'Are you sure you want to quit Scribe?\n\n(Close without Shift to minimize to system tray)',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if hasattr(self, 'tray_icon'):
                    self.tray_icon.hide()
                event.accept()
                QApplication.quit()
            else:
                event.ignore()
        else:
            # Normal close - minimize to tray
            event.ignore()
            self.hide()
            
            # Show tray notification first time
            if not hasattr(self, '_tray_notification_shown'):
                self.tray_icon.showMessage(
                    "Scribe is still running",
                    "Scribe is minimized to system tray. Double-click the icon to restore.\n\nHold Shift when closing to quit completely.",
                    QSystemTrayIcon.Information,
                    3000
                )
                self._tray_notification_shown = True
    
    # ==================== App Integration Methods ====================
    
    def on_transcription_started(self):
        """Handle transcription started signal from app"""
        # Update home page status
        if hasattr(self.home_page, 'update_status'):
            self.home_page.update_status(recording=False)  # Transcribing state
    
    def on_transcription_completed(self, text: str):
        """Handle transcription completed signal from app"""
        # Update home page status
        if hasattr(self.home_page, 'update_status'):
            self.home_page.update_status(recording=False)
        
        # Add to history
        from datetime import datetime
        entry = {
            "timestamp": datetime.now(),
            "text": text,
            "application": "Unknown",
            "window_title": "",
            "audio_duration": 0.0,
            "word_count": len(text.split()),
            "character_count": len(text),
            "confidence": None
        }
        self.add_transcription_event(entry)
        
        # Note: FloatingRecordingWidget handles visual feedback - no InfoBar needed
    
    def on_transcription_failed(self, error: str):
        """Handle transcription failed signal from app"""
        # Update home page status
        if hasattr(self.home_page, 'update_status'):
            self.home_page.update_status(recording=False)
        
        # Note: FloatingRecordingWidget handles visual feedback - no InfoBar needed
        # Errors are already logged to console for debugging

    def update_transcription_summary(self, summary):
        """Relay analytics summary to insights page."""
        if hasattr(self.insights_page, 'update_summary'):
            self.insights_page.update_summary(summary)

    def add_transcription_event(self, entry: dict):
        """Append a transcription history entry to the UI."""
        # Add to dedicated history page
        if hasattr(self.history_page, 'add_transcription'):
            self.history_page.add_transcription(entry)
        
        # Update insights with new data
        if hasattr(self.insights_page, 'add_event'):
            self.insights_page.add_event(entry)

    def update_audio_level(self, level: float):
        """Update audio level - could show on home page in future."""
        pass  # Removed - no longer used
    
    def update_hotkey_status(self, active: bool):
        """Update UI to show hotkey was detected"""
        # Disabled - the floating recording widget provides all visual feedback
        pass
    
    def update_recording_status(self, recording: bool):
        """Update UI to show recording status"""
        if hasattr(self.home_page, 'update_status'):
            self.home_page.update_status(recording=recording)
        
        # Update floating recording widget
        if recording:
            self.recording_widget.start_recording()
            self.recording_widget.position_at_bottom_right(self)
        else:
            self.recording_widget.finish()
    
    def update_transcription_status(self, status: str):
        """Update transcription status on home page"""
        status_map = {
            "idle": False,
            "recording": True,
            "transcribing": False,
            "error": False
        }
        recording = status_map.get(status, False)
        
        if hasattr(self.home_page, 'update_status'):
            self.home_page.update_status(recording=recording)
        
        # Update floating widget for transcribing state
        if status == "transcribing":
            self.recording_widget.start_transcribing()
        elif status == "idle":
            self.recording_widget.finish()

    def _on_test_audio(self):
        """Handle test audio button click"""
        self.test_audio_requested.emit()
        InfoBar.info(
            title="Testing Audio",
            content="Recording 3 seconds of audio...",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self
        )


def main():
    """Entry point for testing the UI"""
    app = QApplication(sys.argv)
    
    # Set app metadata
    app.setApplicationName("Scribe")
    app.setOrganizationName("Scribe Voice")
    app.setApplicationVersion(SCRIBE_VERSION)
    
    # Set app icon early (for taskbar)
    from pathlib import Path
    from PyQt5.QtGui import QIcon
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    assets_dir = project_root / 'assets'
    
    # Windows needs .ico for taskbar
    icon_path = assets_dir / 'scribe-icon.ico'
    if icon_path.exists():
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)
        print(f"✅ Loaded icon from: {icon_path}")
    else:
        # Try PNG as fallback
        icon_path = assets_dir / 'scribe-icon.png'
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            app.setWindowIcon(icon)
            print(f"✅ Loaded icon from: {icon_path}")
        else:
            print(f"⚠️  Icon not found in: {assets_dir}")
    
    window = ScribeMainWindow()
    window.show()
    window.raise_()  # Bring window to front
    window.activateWindow()  # Give it focus
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
