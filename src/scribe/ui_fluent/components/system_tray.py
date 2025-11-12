"""
System tray implementation with proper error handling.
"""

import logging
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal as Signal

logger = logging.getLogger(__name__)

class ScribeSystemTray(QSystemTrayIcon):
    """
    System tray icon with fallback handling for WSL/Linux.
    """
    
    clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_tray()
    
    def _setup_tray(self):
        """Initialize system tray with error handling."""
        try:
            # Set default icon
            icon = QIcon.fromTheme("audio-input-microphone")
            self.setIcon(icon)
            
            # Create context menu
            menu = QMenu()
            
            # Add menu items
            show_action = menu.addAction("Show Scribe")
            show_action.triggered.connect(self.clicked.emit)
            
            menu.addSeparator()
            
            quit_action = menu.addAction("Quit")
            quit_action.triggered.connect(self._quit_app)
            
            self.setContextMenu(menu)
            
            # Try to show tray icon
            self._show_with_fallback()
            
        except Exception as e:
            logger.error(f"Failed to setup system tray: {e}")
            self._setup_fallback()
    
    def _show_with_fallback(self):
        """Attempt to show tray icon with fallback."""
        try:
            # First try standard tray
            if self.isSystemTrayAvailable():
                self.show()
                return True
                
            # Check if we're in WSL
            import os
            if 'WSL_DISTRO_NAME' in os.environ:
                # Try XDG notification daemon
                import subprocess
                subprocess.run(['notify-send', 'Scribe', 'Running in system tray'])
                self.show()
                return True
                
            logger.warning("System tray not available")
            return False
            
        except Exception as e:
            logger.error(f"Error showing tray icon: {e}")
            return False
    
    def _setup_fallback(self):
        """Setup minimal fallback tray support."""
        try:
            # Create basic menu
            menu = QMenu()
            quit_action = menu.addAction("Quit")
            quit_action.triggered.connect(self._quit_app)
            self.setContextMenu(menu)
            
            # Try to show
            self.show()
            
        except Exception as e:
            logger.error(f"Failed to setup fallback tray: {e}")
    
    def _quit_app(self):
        """Quit the application."""
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()