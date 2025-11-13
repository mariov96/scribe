"""
Completion Page - Final success page of the Setup Wizard.

Congratulates user and provides next steps.
"""

from typing import Optional, Dict
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from qfluentwidgets import (
    CardWidget, BodyLabel, TitleLabel, StrongBodyLabel, IconWidget, FluentIcon
)

from .base_page import BasePage, ValidationState


class CompletionPage(BasePage):
    """
    Completion page congratulating user on finishing setup.
    
    Displays:
    - Success message
    - Summary of configured settings
    - Next steps to start using Scribe
    """
    
    def __init__(self, parent: Optional[QLabel] = None):
        self.wizard_data: Dict = {}
        super().__init__(parent)
    
    def setup_ui(self):
        """Set up the completion page UI."""
        super().setup_ui()
        
        # Main content card
        main_card = CardWidget(self)
        card_layout = QVBoxLayout(main_card)
        card_layout.setContentsMargins(60, 50, 60, 50)
        card_layout.setSpacing(24)
        
        # Success icon
        icon_widget = IconWidget(FluentIcon.COMPLETED, main_card)
        icon_widget.setFixedSize(64, 64)
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(icon_widget)
        icon_layout.addStretch()
        card_layout.addLayout(icon_layout)
        
        card_layout.addSpacing(20)
        
        # Success title
        success_title = TitleLabel("You're All Set!", main_card)
        success_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(success_title)
        
        # Success message
        success_message = BodyLabel(
            "Congratulations! Scribe is now configured and ready to boost your productivity.",
            main_card
        )
        success_message.setWordWrap(True)
        success_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_message.setStyleSheet("font-size: 14px; line-height: 1.6; padding: 0 20px;")
        card_layout.addWidget(success_message)
        
        # Divider
        card_layout.addSpacing(16)
        
        # Configuration summary section
        summary_title = StrongBodyLabel("Your Configuration:", main_card)
        summary_title.setStyleSheet("font-size: 15px;")
        card_layout.addWidget(summary_title)
        
        card_layout.addSpacing(4)
        
        # Summary container (will be populated in on_page_enter)
        self.summary_container = QVBoxLayout()
        self.summary_container.setSpacing(8)
        card_layout.addLayout(self.summary_container)
        
        # Next steps section
        card_layout.addSpacing(20)
        next_steps_title = StrongBodyLabel("Next Steps:", main_card)
        next_steps_title.setStyleSheet("font-size: 15px;")
        card_layout.addWidget(next_steps_title)
        
        card_layout.addSpacing(4)
        
        # Next steps
        steps = [
            ("1️⃣", "Press your hotkey to start recording"),
            ("2️⃣", "Speak clearly into your microphone"),
            ("3️⃣", "Release the hotkey to stop and transcribe"),
            ("4️⃣", "Watch your words appear instantly!")
        ]
        
        for emoji, step in steps:
            step_card = self._create_step_card(emoji, step, main_card)
            card_layout.addWidget(step_card)
        
        # Final encouragement
        card_layout.addSpacing(12)
        encouragement = BodyLabel(
            "Ready to transform your workflow? Let's go! 🚀",
            main_card
        )
        encouragement.setAlignment(Qt.AlignmentFlag.AlignCenter)
        encouragement.setStyleSheet("color: #6750A4; font-weight: bold; font-size: 15px; padding: 8px 0;")
        card_layout.addWidget(encouragement)
        
        # Add main card to page layout
        self.layout.addWidget(main_card)
        self.layout.addStretch()
        
        # This page is always valid
        self.set_validation_state(ValidationState.VALID, "Setup complete")
    
    def _create_step_card(self, emoji: str, text: str, parent) -> CardWidget:
        """
        Create a next step card.
        
        Args:
            emoji: Step emoji
            text: Step text
            parent: Parent widget
            
        Returns:
            CardWidget: Step card widget
        """
        card = CardWidget(parent)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)
        
        # Emoji
        emoji_label = QLabel(emoji, card)
        emoji_label.setStyleSheet("font-size: 20px;")
        emoji_label.setFixedSize(32, 32)
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(emoji_label)
        
        # Text
        text_label = BodyLabel(text, card)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("font-size: 13px; line-height: 1.5;")
        layout.addWidget(text_label, 1)
        
        return card
    
    def _create_summary_item(self, icon: str, label: str, value: str, parent) -> CardWidget:
        """
        Create a configuration summary item.
        
        Args:
            icon: Item icon
            label: Setting label
            value: Setting value
            parent: Parent widget
            
        Returns:
            CardWidget: Summary item widget
        """
        card = CardWidget(parent)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(6)
        
        # Top row with icon and label
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        
        icon_label = QLabel(icon, card)
        icon_label.setStyleSheet("font-size: 18px;")
        icon_label.setFixedSize(28, 28)
        top_layout.addWidget(icon_label)
        
        label_text = StrongBodyLabel(label, card)
        label_text.setStyleSheet("font-size: 14px;")
        top_layout.addWidget(label_text, 1)
        
        layout.addLayout(top_layout)
        
        # Value
        value_label = BodyLabel(value, card)
        value_label.setWordWrap(True)
        value_label.setStyleSheet("color: #666; margin-left: 36px; font-size: 13px; line-height: 1.5;")
        layout.addWidget(value_label)
        
        return card
    
    def set_wizard_data(self, data: Dict):
        """
        Set the collected wizard data for display.
        
        Args:
            data: Dictionary of all collected configuration data
        """
        self.wizard_data = data
    
    def validate(self) -> bool:
        """
        Validate the page.
        
        Returns:
            bool: Always True for completion page
        """
        return True
    
    def validate_async(self) -> bool:
        """
        Perform asynchronous validation if needed.
        
        Returns:
            bool: True if async validation was started
        """
        # Completion page doesn't need async validation
        return False
    
    def get_data(self) -> dict:
        """
        Get configuration data.
        
        Returns:
            dict: Setup completion flag
        """
        return {
            'setup_complete': True
        }
    
    def get_title(self) -> str:
        """Get the page title."""
        return "Setup Complete!"
    
    def get_description(self) -> str:
        """Get the page description."""
        return "Scribe is ready to transform your productivity with voice automation."
    
    def on_page_enter(self):
        """Called when the page becomes visible."""
        # Clear previous summary
        while self.summary_container.count():
            item = self.summary_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Populate summary with actual data
        if self.wizard_data:
            # Audio device
            if 'audio_device' in self.wizard_data:
                device_name = self.wizard_data.get('audio_device', 'Unknown')
                summary_item = self._create_summary_item(
                    "🎤",
                    "Microphone",
                    device_name,
                    self.parent()
                )
                self.summary_container.addWidget(summary_item)
            
            # Hotkey
            if 'hotkey' in self.wizard_data:
                hotkey = self.wizard_data.get('hotkey', 'Unknown')
                # Format hotkey for display
                formatted_hotkey = self._format_hotkey(hotkey)
                summary_item = self._create_summary_item(
                    "⌨️",
                    "Hotkey",
                    formatted_hotkey,
                    self.parent()
                )
                self.summary_container.addWidget(summary_item)
            
            # Privacy settings
            privacy_item = self._create_summary_item(
                "🔒",
                "Privacy",
                "100% Local - Your data stays on your device",
                self.parent()
            )
            self.summary_container.addWidget(privacy_item)
        
        # Ensure validation is set
        self.set_validation_state(ValidationState.VALID, "Setup complete")
    
    def on_page_leave(self):
        """Called when leaving the page."""
        # Cancel any pending validation
        self._cancel_async_validation()
    
    def cleanup(self):
        """Clean up page resources."""
        super().cleanup()
    
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
