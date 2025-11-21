"""
Plugins Page - Manage and configure Scribe plugins.
"""

import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import (
    TitleLabel,
    CardWidget,
    BodyLabel,
    StrongBodyLabel,
    ScrollArea
)

from scribe.plugins import PluginRegistry

logger = logging.getLogger(__name__)

class PluginsPage(ScrollArea):
    """A page to display and manage installed plugins."""

    def __init__(self, plugin_registry: PluginRegistry, parent=None):
        super().__init__(parent)
        self.setObjectName("PluginsPage")
        
        self.plugin_registry = plugin_registry
        
        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        
        main_layout = QVBoxLayout(self.view)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)
        
        # Header
        title = TitleLabel("Plugins")
        subtitle = BodyLabel("Extend Scribe's functionality with community-built plugins.")
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        
        # Plugin list
        self.plugin_list_layout = QVBoxLayout()
        main_layout.addLayout(self.plugin_list_layout)
        
        main_layout.addStretch()

        self.refresh_plugins()

    def refresh_plugins(self):
        """Clear and repopulate the list of plugins."""
        # Clear existing widgets
        while self.plugin_list_layout.count():
            child = self.plugin_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        plugins = self.plugin_registry.list_plugins()
        
        if not plugins:
            self.plugin_list_layout.addWidget(BodyLabel("No plugins found."))
            return
            
        for plugin_meta in plugins:
            card = self._create_plugin_card(plugin_meta)
            self.plugin_list_layout.addWidget(card)

    def _create_plugin_card(self, plugin_meta: dict) -> CardWidget:
        """Create a card to display plugin information."""
        card = CardWidget()
        layout = QVBoxLayout(card)
        
        name = plugin_meta.get('name', 'Unknown Plugin')
        version = plugin_meta.get('version', '0.0.0')
        description = plugin_meta.get('description', 'No description available.')
        
        title_label = StrongBodyLabel(f"{name} v{version}")
        description_label = BodyLabel(description)
        
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        
        return card
