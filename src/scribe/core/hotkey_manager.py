"""
Hotkey Manager - Global hotkey detection using keyboard library.
"""

import logging
import platform
import time
import os
import subprocess
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal as Signal
import keyboard

logger = logging.getLogger(__name__)


class HotkeyManager(QObject):
    """
    Hotkey manager using keyboard/pynput for global hotkey detection.
    """

    hotkey_pressed = Signal()
    hotkey_released = Signal(float)

    def __init__(self, config=None):
        """Initialize hotkey manager."""
        super().__init__()
        self.config = config or {}
        self.is_listening = False
        self._hotkey_combo = None
        self._last_trigger_time = 0
        self._debounce_delay = 0.5  # 500ms debounce
        self._keyboard_hotkey = None
        self._keyboard_hold_hotkey = None
        self._pynput_listener = None
        self._pynput_pressed_keys = set()
        self._combo_keys = set()
        self._combo_active = False
        self._hold_start_time = 0.0
        self._pynput_combo_armed = False

        # Get hotkey from config
        try:
            activation_key = config.get('recording_options', 'activation_key', default='ctrl+alt')
            # Convert legacy meta value to windows if present for UI consistency
            self._hotkey_combo = activation_key.replace('meta', 'windows')
            logger.info(f"Hotkey configured: {self._hotkey_combo}")
        except Exception as e:
            logger.error(f"Error getting hotkey from config: {e}")
            self._hotkey_combo = 'ctrl+alt'  # Default

        self._combo_keys = self._parse_combo(self._hotkey_combo)
        self._pynput_combo_armed = False

    def start(self):
        """Start listening for hotkeys."""
        if self.is_listening:
            return

        try:
            logger.info(f"Starting hotkey listener for: {self._hotkey_combo}")
            
            in_wsl = 'WSL_DISTRO_NAME' in os.environ
            system = platform.system().lower()
            
            if in_wsl:
                logger.info("WSL environment detected - using X11 hotkey method")
                self._setup_x11_hotkeys()
            else:
                keyboard_registered = self._start_keyboard_hotkey()
                if system == "windows":
                    # Always start pynput listener so Ctrl/Alt combos work without admin
                    if not keyboard_registered:
                        logger.info("keyboard hook unavailable; relying on pynput listener")
                    self._start_pynput_listener()

            self.is_listening = True
            logger.info("Hotkey listener started successfully")

        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}", exc_info=True)

    def _start_keyboard_hotkey(self) -> bool:
        """Register hotkey using keyboard library."""
        try:
            self._keyboard_hold_hotkey = keyboard.add_hotkey(
                self._hotkey_combo,
                self._on_keyboard_pressed,
                suppress=False,
                trigger_on_release=False,
            )
            self._keyboard_hotkey = keyboard.add_hotkey(
                self._hotkey_combo,
                self._on_keyboard_released,
                suppress=False,
                trigger_on_release=True,
            )
            logger.debug("keyboard library hotkey registered")
            return True
        except Exception as e:
            logger.warning(f"keyboard hotkey registration failed: {e}")
            self._keyboard_hotkey = None
            self._keyboard_hold_hotkey = None
            return False

    def _start_pynput_listener(self):
        """Start a pynput listener for systems where keyboard hooks fail silently."""
        try:
            from pynput import keyboard as pynput_keyboard
        except ImportError as e:
            logger.warning(f"pynput not available, skipping secondary listener: {e}")
            return

        combo = self._combo_keys
        if not combo:
            logger.warning("No parsed combo keys available for pynput listener")
            return

        self._pynput_combo_armed = False

        def on_press(key):
            name = self._normalize_key_name(key)
            if not name:
                return
            self._pynput_pressed_keys.add(name)
            if self._combo_keys and self._combo_keys.issubset(self._pynput_pressed_keys):
                self._pynput_combo_armed = True
                self._handle_hotkey_pressed()

        def on_release(key):
            name = self._normalize_key_name(key)
            if name and name in self._pynput_pressed_keys:
                self._pynput_pressed_keys.discard(name)
            if self._pynput_combo_armed and not (self._combo_keys & self._pynput_pressed_keys):
                self._pynput_combo_armed = False
                self._handle_hotkey_released()

        self._pynput_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
        self._pynput_listener.start()
        logger.debug("pynput listener started for hotkey detection")

    def _parse_combo(self, combo: str) -> set[str]:
        """Parse hotkey combo string into normalized key names."""
        if not combo:
            return set()
        normalized = set()
        for part in combo.split('+'):
            name = part.strip().lower()
            alias = self._alias_map().get(name, name)
            if alias:
                normalized.add(alias)
        return normalized

    def _normalize_key_name(self, key) -> str:
        """Normalize pynput key objects to our alias map."""
        try:
            from pynput import keyboard as pynput_keyboard
        except ImportError:
            return ""

        alias_map = self._alias_map()

        if isinstance(key, pynput_keyboard.KeyCode):
            if key.char:
                return alias_map.get(key.char.lower(), key.char.lower())
            return ""

        key_name = getattr(key, "name", str(key).replace("Key.", "")).lower()
        return alias_map.get(key_name, key_name)

    @staticmethod
    def _alias_map() -> dict[str, str]:
        """Return mapping of alias key names."""
        return {
            "control": "ctrl",
            "ctrl_l": "ctrl",
            "ctrl_r": "ctrl",
            "shift_l": "shift",
            "shift_r": "shift",
            "alt_l": "alt",
            "alt_r": "alt",
            "option": "alt",
            "command": "meta",
            "cmd": "meta",
            "meta": "meta",
            "windows": "windows",
            "win": "windows",
            "super": "windows",
            "space": "space",
        }

    def _setup_x11_hotkeys(self):
        """Setup X11 hotkeys for WSL environment."""
        try:
            try:
                from Xlib import X, XK, display
                from Xlib.display import Display
            except ImportError:
                subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-xlib'], check=True)
                from Xlib import X, XK, display
                from Xlib.display import Display

            def monitor_x11_hotkeys():
                try:
                    disp = Display()
                    root = disp.screen().root
                    root.change_attributes(event_mask=X.KeyPressMask | X.KeyReleaseMask)

                    ctrl_pressed = False
                    super_pressed = False

                    while self.is_listening:
                        event = disp.next_event()

                        if event.type == X.KeyPress:
                            keysym = disp.keycode_to_keysym(event.detail, 0)
                            if keysym in (XK.XK_Control_L, XK.XK_Control_R):
                                ctrl_pressed = True
                            elif keysym in (XK.XK_Super_L, XK.XK_Super_R):
                                super_pressed = True

                            if ctrl_pressed and super_pressed:
                                self._handle_hotkey_pressed()

                        elif event.type == X.KeyRelease:
                            keysym = disp.keycode_to_keysym(event.detail, 0)
                            if keysym in (XK.XK_Control_L, XK.XK_Control_R):
                                ctrl_pressed = False
                            elif keysym in (XK.XK_Super_L, XK.XK_Super_R):
                                super_pressed = False

                            if not (ctrl_pressed and super_pressed):
                                self._handle_hotkey_released()

                except Exception as e:
                    logger.error(f"X11 hotkey error: {e}")
                    self._setup_fallback_hotkeys()

            self._monitor_thread = Thread(target=monitor_x11_hotkeys, daemon=True)
            self._monitor_thread.start()

        except Exception as e:
            logger.error(f"Failed to setup X11 hotkeys: {e}")
            self._setup_fallback_hotkeys()

    def _setup_fallback_hotkeys(self):
        """Fallback to simple hotkey monitoring."""
        try:
            def check_key_combo():
                try:
                    while self.is_listening:
                        result = subprocess.run(
                            ['xdotool', 'getwindowfocus', 'getwindowname'],
                            capture_output=True, text=True
                        )

                        if 'error' not in result.stderr.lower():
                            self._handle_hotkey_pressed()
                        else:
                            self._handle_hotkey_released()

                        time.sleep(0.1)

                except Exception as e:
                    logger.error(f"Fallback hotkey error: {e}")

            self._fallback_thread = Thread(target=check_key_combo, daemon=True)
            self._fallback_thread.start()

        except Exception as e:
            logger.error(f"Failed to setup fallback hotkeys: {e}")
            raise
    
    def stop(self):
        """Stop listening for hotkeys."""
        if not self.is_listening:
            return

        try:
            logger.info("Stopping hotkey listener...")

            # Unregister the keyboard hotkeys
            if self._keyboard_hotkey is not None:
                keyboard.remove_hotkey(self._keyboard_hotkey)
                self._keyboard_hotkey = None
            if self._keyboard_hold_hotkey is not None:
                keyboard.remove_hotkey(self._keyboard_hold_hotkey)
                self._keyboard_hold_hotkey = None

            # Stop pynput listener if running
            if self._pynput_listener:
                self._pynput_listener.stop()
                self._pynput_listener = None
                self._pynput_pressed_keys.clear()

            self.is_listening = False
            logger.info("Hotkey listener stopped")

        except Exception as e:
            logger.error(f"Error stopping hotkey listener: {e}", exc_info=True)

    def _on_keyboard_pressed(self):
        self._handle_hotkey_pressed()

    def _on_keyboard_released(self):
        self._handle_hotkey_released()

    def _handle_hotkey_pressed(self):
        logger.debug("[HOTKEY] pressed")
        if self._combo_active:
            logger.debug("[HOTKEY] combo already active, ignoring")
            return
        self._combo_active = True
        self._hold_start_time = time.time()
        logger.debug("[HOTKEY] emitting hotkey_pressed")
        self.hotkey_pressed.emit()
        logger.debug("[HOTKEY] signal emitted")

    def _handle_hotkey_released(self):
        if not self._combo_active:
            return
        self._combo_active = False
        duration = time.time() - self._hold_start_time if self._hold_start_time else 0.0
        self.hotkey_released.emit(max(0.0, duration))
        logger.debug("[HOTKEY] released (%.0f ms)" % (duration*1000))
