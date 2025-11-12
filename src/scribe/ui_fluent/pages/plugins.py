"""
Plugins Page - Plugin management interface
"""

from typing import Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel,
    LineEdit, PrimaryPushButton, FluentIcon as FIF, isDarkTheme,
    MessageBox
)

from ..branding import get_contrasting_color
from ..widgets import PluginCard


class PluginsPage(ScrollArea):
    """Plugin management"""
    
    def __init__(self, plugin_registry=None, config_manager=None, parent=None):
        super().__init__(parent)
        self.setObjectName("PluginsPage")
        
        self.plugin_registry = plugin_registry
        self.config_manager = config_manager
        
        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        
        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(24)
        
        title = TitleLabel("Plugins")
        subtitle = BodyLabel("Extend Scribe with custom voice commands and automations")
        is_dark = isDarkTheme()
        subtitle.setTextColor(get_contrasting_color(is_dark), get_contrasting_color(is_dark))
        
        filter_row = QHBoxLayout()
        search_box = LineEdit()
        search_box.setPlaceholderText("Search plugins...")
        search_box.setClearButtonEnabled(True)
        search_box.setFixedWidth(300)
        
        add_btn = PrimaryPushButton(FIF.ADD, "Install Plugin")
        
        filter_row.addWidget(search_box)
        filter_row.addStretch()
        filter_row.addWidget(add_btn)
        
        plugins_label = SubtitleLabel("Installed Plugins")
        
        self.plugins_container = QWidget()
        self.plugins_layout = QVBoxLayout(self.plugins_container)
        self.plugins_layout.setSpacing(16)
        self.plugins_layout.setContentsMargins(0, 0, 0, 0)
        
        # Load plugins from registry or use samples
        if self.plugin_registry:
            self._load_real_plugins()
        else:
            self._add_sample_plugins()
        
        self.vBoxLayout.addWidget(title)
        self.vBoxLayout.addWidget(subtitle)
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addLayout(filter_row)
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addWidget(plugins_label)
        self.vBoxLayout.addWidget(self.plugins_container)
        self.vBoxLayout.addStretch(1)
    
    def _load_real_plugins(self):
        """Load plugins from the plugin registry."""
        # Get list of enabled plugins from config
        enabled_plugins = set()
        if self.config_manager:
            try:
                enabled_plugins = set(self.config_manager.config.plugins.enabled_plugins)
            except:
                pass
        
        # Get all registered plugins
        plugins = self.plugin_registry.list_plugins()
        
        for plugin_meta in plugins:
            plugin_id = plugin_meta.get('name', '').lower().replace(' ', '_')
            name = plugin_meta.get('name', 'Unknown')
            description = plugin_meta.get('description', 'No description available')
            enabled = plugin_id in enabled_plugins
            
            card = PluginCard(
                plugin_id,
                name,
                description,
                enabled
            )
            card.toggled.connect(self._on_plugin_toggled)
            card.configureClicked.connect(self._on_plugin_configure)
            self.plugins_layout.addWidget(card)
    
    def _on_plugin_toggled(self, plugin_id: str, enabled: bool):
        """Handle plugin enable/disable toggle."""
        if not self.config_manager:
            return
        
        try:
            # Update config
            if enabled:
                # Add to enabled plugins
                if plugin_id not in self.config_manager.config.plugins.enabled_plugins:
                    self.config_manager.config.plugins.enabled_plugins.append(plugin_id)
            else:
                # Remove from enabled plugins
                if plugin_id in self.config_manager.config.plugins.enabled_plugins:
                    self.config_manager.config.plugins.enabled_plugins.remove(plugin_id)
            
            # Save config
            self.config_manager.save()
            
            # Hot reload plugin if registry is available
            if self.plugin_registry:
                try:
                    if enabled:
                        # Load/enable the plugin
                        # Note: Actual plugin loading would need plugin path/module info
                        self.plugin_registry.enable_plugin(plugin_id)
                    else:
                        # Unload/disable the plugin
                        self.plugin_registry.disable_plugin(plugin_id)
                except AttributeError:
                    # Registry doesn't have enable/disable methods yet
                    pass  # Config is still saved, will apply on restart
                except Exception as e:
                    # Show error if hot-reload fails
                    MessageBox(
                        "Plugin Reload",
                        f"Plugin {'enabled' if enabled else 'disabled'}.\n"
                        f"Changes will take effect on restart.\n\n"
                        f"Hot-reload not yet implemented.",
                        self
                    ).exec()
                    return
            
        except Exception as e:
            # Show error message
            MessageBox(
                "Error",
                f"Failed to {'enable' if enabled else 'disable'} plugin: {str(e)}",
                self
            ).exec()
    
    def _on_plugin_configure(self, plugin_id: str):
        """Handle plugin configuration button click."""
        # Get plugin details from registry
        plugin_name = plugin_id.replace('_', ' ').title()
        plugin_info = None
        
        if self.plugin_registry:
            plugins = self.plugin_registry.list_plugins()
            for p in plugins:
                if p.get('name', '').lower().replace(' ', '_') == plugin_id:
                    plugin_info = p
                    break
        
        # Show configuration dialog
        from qfluentwidgets import MessageBox, Dialog
        
        dialog = MessageBox(
            f"Configure {plugin_name}",
            f"Plugin configuration coming soon!\n\n"
            f"Future features:\n"
            f"• Custom command patterns\n"
            f"• Keyboard shortcuts\n"
            f"• Plugin-specific settings\n"
            f"• Priority configuration",
            self
        )
        dialog.exec()
    
    def _add_sample_plugins(self):
        """Add sample plugins for demo purposes."""
        plugins = [
            {"id": "window_manager", "name": "Window Manager", 
             "description": "Control windows with voice: minimize, maximize, close, switch between apps", 
             "enabled": True},
            {"id": "code_snippets", "name": "Code Snippets", 
             "description": "Insert programming templates and boilerplate with voice commands", 
             "enabled": True},
            {"id": "email_composer", "name": "Email Composer", 
             "description": "Compose and send emails hands-free with natural voice commands", 
             "enabled": False},
            {"id": "browser_control", "name": "Browser Control", 
             "description": "Navigate web pages, open tabs, search, and control media playback", 
             "enabled": True},
            {"id": "text_formatting", "name": "Text Formatting", 
             "description": "Apply formatting: bold, italic, bullet points, headings, and more", 
             "enabled": True},
            {"id": "calendar", "name": "Calendar Integration", 
             "description": "Create events, check schedule, and manage appointments with voice", 
             "enabled": False},
        ]
        
        for plugin_data in plugins:
            card = PluginCard(
                plugin_data["id"],
                plugin_data["name"],
                plugin_data["description"],
                plugin_data["enabled"]
            )
            card.toggled.connect(self._on_plugin_toggled)
            card.configureClicked.connect(self._on_plugin_configure)
            self.plugins_layout.addWidget(card)
