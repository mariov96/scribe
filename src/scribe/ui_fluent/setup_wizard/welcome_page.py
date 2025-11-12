"""
Welcome Page - First page of the Setup Wizard.

Introduces Scribe and sets expectations for the setup process.
"""

from typing import Optional
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from qfluentwidgets import (
    CardWidget, BodyLabel, TitleLabel, 
    StrongBodyLabel, IconWidget, FluentIcon
)

from .base_page import BasePage, ValidationState


class WelcomePage(BasePage):
    """
    Welcome page introducing Scribe and the setup process.
    
    This is an informational page that always validates as true.
    """
    
    def setup_ui(self):
        """Set up the welcome page UI."""
        super().setup_ui()
        
        # Main content card
        main_card = CardWidget(self)
        card_layout = QVBoxLayout(main_card)
        card_layout.setContentsMargins(60, 50, 60, 50)
        card_layout.setSpacing(0)  # We'll manually control all spacing
        
        # Welcome icon/logo
        icon_widget = IconWidget(FluentIcon.MICROPHONE, main_card)
        icon_widget.setFixedSize(64, 64)
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(icon_widget)
        icon_layout.addStretch()
        card_layout.addLayout(icon_layout)
        
        # Space between icon and title
        card_layout.addSpacing(28)
        
        # Welcome title
        welcome_title = TitleLabel("Welcome to Scribe!", main_card)
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_title.setStyleSheet("font-size: 26px; padding: 8px 0px;")
        card_layout.addWidget(welcome_title)
        
        # Space between title and description
        card_layout.addSpacing(20)
        
        # Description
        description = BodyLabel(
            "Scribe is your privacy-first voice automation platform. "
            "Transform your voice into text, control your computer hands-free, "
            "and boost your productivity—all while keeping your data local.",
            main_card
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet(
            "font-size: 15px; "
            "line-height: 28px; "
            "padding: 8px 40px 12px 40px; "
            "min-height: 90px;"
        )
        card_layout.addWidget(description)
        
        # Space before config section
        card_layout.addSpacing(64)
        
        # What we'll configure section
        config_title = StrongBodyLabel("What We'll Set Up:", main_card)
        config_title.setStyleSheet("font-size: 15px; font-weight: 600;")
        card_layout.addWidget(config_title)
        
        # Space after section title
        card_layout.addSpacing(20)
        
        # Configuration items
        config_items = [
            (FluentIcon.MICROPHONE, "Audio Device", "Select your microphone for voice input"),
            (FluentIcon.EDIT, "Global Hotkey", "Configure your recording activation key"),
            (FluentIcon.SETTING, "Preferences", "Personalize your Scribe experience")
        ]
        
        for icon, title, desc in config_items:
            item_widget = self._create_config_item(icon, title, desc, main_card)
            card_layout.addWidget(item_widget)
            card_layout.addSpacing(8)  # Space between config items
        
        # Space before ready message
        card_layout.addSpacing(48)
        
        # Ready message
        ready_label = BodyLabel(
            "This will only take a few minutes. Let's get started!",
            main_card
        )
        ready_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ready_label.setStyleSheet(
            "color: #6750A4; "
            "font-weight: bold; "
            "font-size: 14px; "
            "padding: 8px 0px;"
        )
        card_layout.addWidget(ready_label)
        
        # Add main card to page layout
        self.layout.addWidget(main_card)
        self.layout.addStretch()
        
        # This page is always valid
        self.set_validation_state(ValidationState.VALID, "Welcome page ready")
    
    def _create_config_item(self, icon: FluentIcon, title: str, description: str, parent) -> CardWidget:
        """
        Create a configuration item widget.
        
        Args:
            icon: FluentIcon for the item
            title: Item title
            description: Item description
            parent: Parent widget
            
        Returns:
            CardWidget: The configuration item widget
        """
        item = CardWidget(parent)
        item.setFixedHeight(88)  # Even taller for better text visibility
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(28, 20, 28, 20)
        item_layout.setSpacing(20)
        
        # Icon
        icon_widget = IconWidget(icon, item)
        icon_widget.setFixedSize(28, 28)
        item_layout.addWidget(icon_widget, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = StrongBodyLabel(title, item)
        title_label.setStyleSheet("font-size: 15px; font-weight: 600; padding-bottom: 2px;")
        text_layout.addWidget(title_label)
        
        # Description
        desc_label = BodyLabel(description, item)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "color: #505050; "
            "font-size: 14px; "
            "line-height: 22px; "
            "padding-top: 2px;"
        )
        text_layout.addWidget(desc_label)
        
        item_layout.addLayout(text_layout, 1)
        
        return item
    
    def validate(self) -> bool:
        """
        Validate the page.
        
        Returns:
            bool: Always True for the welcome page
        """
        return True
    
    def validate_async(self) -> bool:
        """
        Perform asynchronous validation if needed.
        
        Returns:
            bool: True if async validation was started
        """
        # Welcome page doesn't need async validation
        return False
    
    def get_data(self) -> dict:
        """
        Get configuration data.
        
        Returns:
            dict: Empty dict as this is an informational page
        """
        return {}
    
    def get_title(self) -> str:
        """Get the page title."""
        return "Welcome to Scribe"
    
    def get_description(self) -> str:
        """Get the page description."""
        return "Let's set up your voice automation platform in just a few steps."
    
    def on_page_enter(self):
        """Called when the page becomes visible."""
        # Ensure validation is set
        self.set_validation_state(ValidationState.VALID, "Welcome page ready")
    
    def on_page_leave(self):
        """Called when leaving the page."""
        # Cancel any pending validation
        self._cancel_async_validation()
    
    def cleanup(self):
        """Clean up page resources."""
        super().cleanup()
