"""
Hotkey Configuration Page - Global hotkey setup.

Allows user to configure the keyboard shortcut for voice recording activation.
"""

from typing import Optional
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal as Signal
from qfluentwidgets import (
    CardWidget, BodyLabel, StrongBodyLabel,
    PushButton, PrimaryPushButton, InfoBar, InfoBarPosition
)
import keyboard

from .base_page import BasePage, ValidationState


class HotkeyConfigPage(BasePage):
    """
    Hotkey configuration page.
    
    Allows user to:
    - View current hotkey (default: Ctrl+Alt)
    - Record a new hotkey combination
    - Validate against system conflicts
    """
    
    def setup_ui(self):
        """Set up the hotkey configuration page UI."""
        super().setup_ui()
        
        self.current_hotkey = "ctrl+alt"  # Default
        self.is_recording_hotkey = False
        self.pressed_keys = set()
        self.hotkey_valid = True  # Default hotkey is valid
        
        # Main content card
        main_card = CardWidget(self)
        card_layout = QVBoxLayout(main_card)
        card_layout.setContentsMargins(60, 50, 60, 50)
        card_layout.setSpacing(24)
        
        # Instructions
        instructions = BodyLabel(
            "Choose a keyboard shortcut to activate voice recording. "
            "This hotkey will work globally across all applications.",
            main_card
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 14px; line-height: 1.6;")
        card_layout.addWidget(instructions)
        
        # Current hotkey display
        card_layout.addSpacing(8)
        current_label = StrongBodyLabel("Current Hotkey:", main_card)
        current_label.setStyleSheet("font-size: 15px;")
        card_layout.addWidget(current_label)
        
        # Hotkey display box
        hotkey_display_card = CardWidget(main_card)
        hotkey_display_layout = QVBoxLayout(hotkey_display_card)
        hotkey_display_layout.setContentsMargins(16, 16, 16, 16)
        
        self.hotkey_display = QLabel(self._format_hotkey(self.current_hotkey), hotkey_display_card)
        self.hotkey_display.setStyleSheet("font-size: 22px; font-weight: bold; color: #6750A4;")
        self.hotkey_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hotkey_display_layout.addWidget(self.hotkey_display)
        
        card_layout.addWidget(hotkey_display_card)
        
        # Record new hotkey button
        card_layout.addSpacing(8)
        self.record_button = PrimaryPushButton("⌨️ Record New Hotkey", main_card)
        self.record_button.clicked.connect(self._start_recording_hotkey)
        card_layout.addWidget(self.record_button)
        
        # Recording instructions (hidden initially)
        self.recording_label = BodyLabel(
            "Press your desired key combination now...",
            main_card
        )
        self.recording_label.setStyleSheet("color: #1976D2; font-weight: bold;")
        self.recording_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recording_label.hide()
        card_layout.addWidget(self.recording_label)
        
        # Cancel button (hidden initially)
        self.cancel_button = PushButton("Cancel", main_card)
        self.cancel_button.clicked.connect(self._cancel_recording)
        self.cancel_button.hide()
        card_layout.addWidget(self.cancel_button)
        
        # Info section
        card_layout.addSpacing(16)
        info_card = CardWidget(main_card)
        info_card.setStyleSheet("background-color: #E3F2FD; border: 1px solid #90CAF9;")
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.setSpacing(8)
        
        info_title = StrongBodyLabel("💡 Tips:", info_card)
        info_title.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(info_title)
        
        tips = [
            "• The hotkey triggers when you RELEASE the keys (not when pressed)",
            "• Use modifier keys (Ctrl, Alt, Shift) for best results",
            "• Avoid common shortcuts like Ctrl+C or Ctrl+V",
            "• The default Ctrl+Alt works well for most users"
        ]
        
        for tip in tips:
            tip_label = BodyLabel(tip, info_card)
            tip_label.setStyleSheet("font-size: 13px; line-height: 1.6;")
            info_layout.addWidget(tip_label)
        
        card_layout.addWidget(info_card)
        
        # Add main card to page layout
        self.layout.addWidget(main_card)
        self.layout.addStretch()
        
        # Page is valid by default (has default hotkey)
        self.set_validation_state(ValidationState.VALID, "Default hotkey configured")
    
    def _format_hotkey(self, hotkey: str) -> str:
        """
        Format hotkey string for display.
        
        Args:
            hotkey: Hotkey string (e.g., 'ctrl+alt')
            
        Returns:
            str: Formatted string (e.g., 'Ctrl + Alt')
        """
        parts = hotkey.split('+')
        formatted_parts = []
        
        for part in parts:
            part = part.strip().lower()
            if part == 'ctrl':
                formatted_parts.append('Ctrl')
            elif part == 'shift':
                formatted_parts.append('Shift')
            elif part == 'alt':
                formatted_parts.append('Alt')
            elif part == 'windows' or part == 'win' or part == 'meta':
                formatted_parts.append('Windows')
            elif part == 'cmd':
                formatted_parts.append('Cmd')
            else:
                formatted_parts.append(part.upper())
        
        return ' + '.join(formatted_parts)
    
    def _start_recording_hotkey(self):
        """Start recording a new hotkey."""
        if self.is_recording_hotkey:
            return
        
        self.is_recording_hotkey = True
        self.pressed_keys = set()
        
        # Update UI
        self.record_button.hide()
        self.recording_label.show()
        self.cancel_button.show()
        self.hotkey_display.setText("Press keys...")
        self.hotkey_display.setStyleSheet("font-size: 20px; font-style: italic; color: #999;")
        
        # Update validation state
        self.set_validation_state(ValidationState.PENDING, "Recording hotkey...")
        
        # Hook keyboard events
        keyboard.hook(self._on_key_event)
    
    def _on_key_event(self, event):
        """
        Handle keyboard events during hotkey recording.
        
        Args:
            event: Keyboard event
        """
        if not self.is_recording_hotkey:
            return
        
        key_name = event.name
        
        if event.event_type == 'down':
            # Add key to pressed set
            self.pressed_keys.add(key_name)
            
            # Update display
            if self.pressed_keys:
                display_text = ' + '.join(sorted(self.pressed_keys))
                self.hotkey_display.setText(self._format_hotkey(display_text))
                self.hotkey_display.setStyleSheet("font-size: 24px; font-weight: bold; color: #6750A4;")
        
        elif event.event_type == 'up' and self.pressed_keys:
            # When keys are released, finalize the hotkey
            if len(self.pressed_keys) >= 1:  # At least one key
                new_hotkey = '+'.join(sorted(self.pressed_keys))
                self._finish_recording(new_hotkey)
    
    def _finish_recording(self, hotkey: str):
        """
        Finish recording and validate the new hotkey.
        
        Args:
            hotkey: The recorded hotkey string
        """
        # Unhook keyboard
        keyboard.unhook_all()
        
        # Validate hotkey
        if self._validate_hotkey(hotkey):
            self.current_hotkey = hotkey
            self.hotkey_valid = True
            self.hotkey_display.setText(self._format_hotkey(hotkey))
            self.hotkey_display.setStyleSheet("font-size: 24px; font-weight: bold; color: #6750A4;")
            self.set_validation_state(ValidationState.VALID, "Hotkey configured successfully")
            
            InfoBar.success(
                title="Hotkey Set",
                content=f"Your hotkey is now: {self._format_hotkey(hotkey)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            # Invalid hotkey, revert to previous
            self.hotkey_valid = False
            self.hotkey_display.setText(self._format_hotkey(self.current_hotkey))
            self.hotkey_display.setStyleSheet("font-size: 24px; font-weight: bold; color: #6750A4;")
            self.set_validation_state(ValidationState.INVALID, "Invalid hotkey combination")
            
            InfoBar.warning(
                title="Invalid Hotkey",
                content="Please use modifier keys (Ctrl, Alt, Shift, Windows) for safety.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            )
        
        # Reset UI
        self.is_recording_hotkey = False
        self.pressed_keys = set()
        self.recording_label.hide()
        self.cancel_button.hide()
        self.record_button.show()
    
    def _cancel_recording(self):
        """Cancel hotkey recording."""
        # Unhook keyboard
        keyboard.unhook_all()
        
        # Reset state
        self.is_recording_hotkey = False
        self.pressed_keys = set()
        
        # Reset UI
        self.hotkey_display.setText(self._format_hotkey(self.current_hotkey))
        self.hotkey_display.setStyleSheet("font-size: 24px; font-weight: bold; color: #6750A4;")
        self.recording_label.hide()
        self.cancel_button.hide()
        self.record_button.show()
        
        # Reset validation state based on current hotkey validity
        if self.hotkey_valid:
            self.set_validation_state(ValidationState.VALID, "Hotkey configured")
        else:
            self.set_validation_state(ValidationState.INVALID, "Please configure a valid hotkey")
    
    def _validate_hotkey(self, hotkey: str) -> bool:
        """
        Validate the hotkey for safety.
        
        Args:
            hotkey: Hotkey to validate
            
        Returns:
            bool: True if valid
        """
        keys = set(k.lower() for k in hotkey.split('+'))
        
        # Require at least one modifier key for safety
        modifiers = {'ctrl', 'alt', 'shift', 'windows', 'win', 'meta', 'cmd'}
        has_modifier = bool(keys & modifiers)
        
        # Check for common system hotkeys to avoid
        dangerous_combos = {
            'ctrl+alt+delete',
            'alt+f4',
            'windows+l',
            'ctrl+shift+esc'
        }
        
        hotkey_normalized = '+'.join(sorted(keys))
        is_dangerous = hotkey_normalized in dangerous_combos
        
        return has_modifier and not is_dangerous
    
    def validate(self) -> bool:
        """
        Validate the page.
        
        Returns:
            bool: True if hotkey is valid
        """
        return self.hotkey_valid and not self.is_recording_hotkey
    
    def validate_async(self) -> bool:
        """
        Perform asynchronous validation if needed.
        
        Returns:
            bool: True if async validation was started
        """
        # For hotkey configuration, we do synchronous validation
        return False
    
    def get_data(self) -> dict:
        """
        Get configuration data.
        
        Returns:
            dict: Hotkey configuration
        """
        return {
            'hotkey': self.current_hotkey,
            'hotkey_formatted': self._format_hotkey(self.current_hotkey)
        }
    
    def get_title(self) -> str:
        """Get the page title."""
        return "Hotkey Configuration"
    
    def get_description(self) -> str:
        """Get the page description."""
        return "Set up your global keyboard shortcut for activating voice recording."
    
    def on_page_enter(self):
        """Called when the page becomes visible."""
        # Ensure validation is set based on current state
        if self.hotkey_valid and not self.is_recording_hotkey:
            self.set_validation_state(ValidationState.VALID, "Hotkey configured")
        elif self.is_recording_hotkey:
            self.set_validation_state(ValidationState.PENDING, "Recording hotkey...")
        else:
            self.set_validation_state(ValidationState.INVALID, "Please configure a valid hotkey")
    
    def on_page_leave(self):
        """Called when leaving the page."""
        # Ensure keyboard hooks are cleaned up
        if self.is_recording_hotkey:
            keyboard.unhook_all()
            self.is_recording_hotkey = False
            self._cancel_recording()
        
        # Cancel any pending validation
        self._cancel_async_validation()
    
    def cleanup(self):
        """Clean up page resources."""
        super().cleanup()
        
        # Ensure keyboard hooks are cleaned up
        if self.is_recording_hotkey:
            keyboard.unhook_all()
            self.is_recording_hotkey = False
