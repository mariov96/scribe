"""
Plugin Card Widget
Displays plugin info with enable/disable toggle
"""

from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    CardWidget, SubtitleLabel, BodyLabel, CaptionLabel,
    SwitchButton, TransparentPushButton, FluentIcon as FIF,
    isDarkTheme
)

from ..branding import get_contrasting_color, get_secondary_color


class PluginCard(CardWidget):
    """Card representing a plugin with enable/disable toggle"""
    
    toggled = Signal(str, bool)
    configureClicked = Signal(str)
    
    def __init__(self, plugin_id: str, name: str, description: str, 
                 enabled: bool = False, has_config: bool = True, parent=None):
        super().__init__(parent)
        self.plugin_id = plugin_id
        self.has_config = has_config
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header row (name + toggle)
        header_layout = QHBoxLayout()
        self.name_label = SubtitleLabel(name)
        self.toggle = SwitchButton()
        self.toggle.setChecked(enabled)
        self.toggle.checkedChanged.connect(self._on_toggled)
        
        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle)
        
        # Description with good contrast
        self.desc_label = BodyLabel(description)
        self.desc_label.setWordWrap(True)
        is_dark = isDarkTheme()
        self.desc_label.setTextColor(get_contrasting_color(is_dark), get_contrasting_color(is_dark))
        
        # Footer
        footer_layout = QHBoxLayout()
        # Configure button hidden for now - feature coming in future release
        # if has_config:
        #     self.config_btn = TransparentPushButton(FIF.SETTING, "Configure")
        #     self.config_btn.clicked.connect(lambda: self.configureClicked.emit(self.plugin_id))
        #     footer_layout.addWidget(self.config_btn)
        footer_layout.addStretch()
        
        # Status indicator
        self.status_label = CaptionLabel("Ready" if enabled else "Disabled")
        status_color = QColor(82, 196, 26) if enabled else get_secondary_color(is_dark)
        self.status_label.setTextColor(status_color, status_color)
        footer_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.desc_label)
        layout.addLayout(footer_layout)
        
        self.setFixedHeight(140)
    
    def _on_toggled(self, checked: bool):
        is_dark = isDarkTheme()
        self.status_label.setText("Ready" if checked else "Disabled")
        status_color = QColor(82, 196, 26) if checked else get_secondary_color(is_dark)
        self.status_label.setTextColor(status_color, status_color)
        self.toggled.emit(self.plugin_id, checked)
