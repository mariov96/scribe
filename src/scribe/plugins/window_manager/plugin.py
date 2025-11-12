"""
Window Manager Plugin - Voice control for Windows applications.

This plugin provides voice commands to control windows and applications on Windows.
Uses pygetwindow for cross-platform window management.

Commands:
- "switch to {app}" - Activate application window
- "minimize" / "minimize {app}" - Minimize window
- "maximize" / "maximize {app}" - Maximize window
- "close window" / "close {app}" - Close application
- "list windows" - Show all open windows
"""

import logging
from typing import List, Dict, Any, Optional

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False

from scribe.plugins.base import BasePlugin, CommandDefinition


logger = logging.getLogger(__name__)


class WindowManager(BasePlugin):
    """
    Plugin for voice-controlled window and application management.

    Allows users to control their desktop environment by voice:
    - Switch between applications quickly
    - Manage window states (minimize/maximize/close)
    - Navigate their workspace hands-free
    """

    # Plugin metadata
    name = "window_manager"
    version = "1.0.0"
    description = "Control windows and applications by voice"
    author = "Scribe Contributors"
    api_version = "2.0"

    def __init__(self):
        """Initialize window manager plugin."""
        self.config: Dict[str, Any] = {}
        self._app_shortcuts: Dict[str, str] = {}

    def commands(self) -> List[CommandDefinition]:
        """
        Define voice commands for window management.

        Returns:
            List of command definitions
        """
        return [
            CommandDefinition(
                patterns=["switch to {app}", "open {app}", "focus {app}"],
                handler=self.switch_to_app,
                examples=[
                    "switch to chrome",
                    "switch to visual studio code",
                    "open spotify"
                ],
                description="Switch focus to specified application"
            ),
            CommandDefinition(
                patterns=["minimize", "minimize window"],
                handler=self.minimize_current,
                examples=["minimize", "minimize window"],
                description="Minimize the currently active window"
            ),
            CommandDefinition(
                patterns=["minimize {app}"],
                handler=self.minimize_app,
                examples=["minimize chrome", "minimize spotify"],
                description="Minimize specified application"
            ),
            CommandDefinition(
                patterns=["maximize", "maximize window"],
                handler=self.maximize_current,
                examples=["maximize", "maximize window"],
                description="Maximize the currently active window"
            ),
            CommandDefinition(
                patterns=["maximize {app}"],
                handler=self.maximize_app,
                examples=["maximize chrome", "maximize code"],
                description="Maximize specified application"
            ),
            CommandDefinition(
                patterns=["close window"],
                handler=self.close_current,
                examples=["close window"],
                description="Close the currently active window"
            ),
            CommandDefinition(
                patterns=["close {app}"],
                handler=self.close_app,
                examples=["close chrome", "close spotify"],
                description="Close specified application"
            ),
            CommandDefinition(
                patterns=["list windows", "show windows", "what's open"],
                handler=self.list_windows,
                examples=["list windows", "show windows", "what's open"],
                description="List all open windows"
            ),
        ]

    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the window manager plugin.

        Args:
            config: Plugin configuration with optional app shortcuts

        Returns:
            True if initialization successful

        Config example:
            {
                "app_shortcuts": {
                    "chrome": "Google Chrome",
                    "code": "Visual Studio Code",
                    "spotify": "Spotify"
                }
            }
        """
        if not PYGETWINDOW_AVAILABLE:
            logger.error("pygetwindow not available. Install with: pip install pygetwindow")
            return False

        self.config = config
        self._app_shortcuts = config.get("app_shortcuts", {})

        logger.info(f"WindowManager initialized with {len(self._app_shortcuts)} app shortcuts")
        return True

    def shutdown(self):
        """Clean up when plugin is unloaded."""
        logger.info("WindowManager plugin shutting down")
        self.config = {}
        self._app_shortcuts = {}

    # ==================== Command Handlers ====================

    def switch_to_app(self, app: str) -> str:
        """
        Switch focus to specified application.

        Args:
            app: Application name (can use shortcut or full title)

        Returns:
            Success message or error
        """
        try:
            # Check if app is a configured shortcut
            app_title = self._app_shortcuts.get(app.lower(), app)

            # Find matching windows
            windows = gw.getWindowsWithTitle(app_title)

            if not windows:
                # Try case-insensitive partial match
                all_windows = gw.getAllTitles()
                matching = [w for w in all_windows if app_title.lower() in w.lower()]

                if matching:
                    windows = [gw.getWindowsWithTitle(matching[0])[0]]
                else:
                    return f"Could not find window: {app}"

            # Activate first matching window
            window = windows[0]
            window.activate()
            logger.info(f"Switched to: {window.title}")
            return f"Switched to {window.title}"

        except Exception as e:
            error_msg = f"Error switching to {app}: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def minimize_current(self) -> str:
        """Minimize the currently active window."""
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                active_window.minimize()
                logger.info(f"Minimized: {active_window.title}")
                return f"Minimized {active_window.title}"
            return "No active window found"
        except Exception as e:
            error_msg = f"Error minimizing window: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def minimize_app(self, app: str) -> str:
        """Minimize specified application."""
        try:
            app_title = self._app_shortcuts.get(app.lower(), app)
            windows = gw.getWindowsWithTitle(app_title)

            if not windows:
                return f"Could not find window: {app}"

            window = windows[0]
            window.minimize()
            logger.info(f"Minimized: {window.title}")
            return f"Minimized {window.title}"

        except Exception as e:
            error_msg = f"Error minimizing {app}: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def maximize_current(self) -> str:
        """Maximize the currently active window."""
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                active_window.maximize()
                logger.info(f"Maximized: {active_window.title}")
                return f"Maximized {active_window.title}"
            return "No active window found"
        except Exception as e:
            error_msg = f"Error maximizing window: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def maximize_app(self, app: str) -> str:
        """Maximize specified application."""
        try:
            app_title = self._app_shortcuts.get(app.lower(), app)
            windows = gw.getWindowsWithTitle(app_title)

            if not windows:
                return f"Could not find window: {app}"

            window = windows[0]
            window.maximize()
            logger.info(f"Maximized: {window.title}")
            return f"Maximized {window.title}"

        except Exception as e:
            error_msg = f"Error maximizing {app}: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def close_current(self) -> str:
        """Close the currently active window."""
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                title = active_window.title
                active_window.close()
                logger.info(f"Closed: {title}")
                return f"Closed {title}"
            return "No active window found"
        except Exception as e:
            error_msg = f"Error closing window: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def close_app(self, app: str) -> str:
        """Close specified application."""
        try:
            app_title = self._app_shortcuts.get(app.lower(), app)
            windows = gw.getWindowsWithTitle(app_title)

            if not windows:
                return f"Could not find window: {app}"

            window = windows[0]
            title = window.title
            window.close()
            logger.info(f"Closed: {title}")
            return f"Closed {title}"

        except Exception as e:
            error_msg = f"Error closing {app}: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def list_windows(self) -> str:
        """List all open windows."""
        try:
            all_titles = gw.getAllTitles()
            # Filter out empty titles
            visible_titles = [t for t in all_titles if t.strip()]

            if not visible_titles:
                return "No windows found"

            # Format as numbered list
            window_list = "\n".join(f"{i+1}. {title}" for i, title in enumerate(visible_titles))
            logger.info(f"Listed {len(visible_titles)} windows")
            return f"Open windows:\n{window_list}"

        except Exception as e:
            error_msg = f"Error listing windows: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # ==================== Helper Methods ====================

    def find_window_fuzzy(self, search_term: str) -> Optional[Any]:
        """
        Find a window using fuzzy matching.

        Args:
            search_term: Term to search for in window titles

        Returns:
            Window object if found, None otherwise
        """
        all_windows = gw.getAllWindows()
        search_lower = search_term.lower()

        # Try exact match first
        for window in all_windows:
            if search_lower == window.title.lower():
                return window

        # Try partial match
        for window in all_windows:
            if search_lower in window.title.lower():
                return window

        return None
