"""
Plugin Registry - Manages plugin loading, discovery, and command routing.

This module provides the central registry for all Scribe plugins.
It handles plugin lifecycle, command registration, and execution.
"""

import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from .base import BasePlugin, CommandDefinition, PluginError


logger = logging.getLogger(__name__)


@dataclass
class RegisteredCommand:
    """A command registered by a plugin with routing information."""
    plugin: BasePlugin
    definition: CommandDefinition
    pattern: str  # Individual pattern from definition.patterns

    def execute(self, **kwargs) -> Any:
        """Execute this command with the given arguments."""
        return self.definition.handler(**kwargs)


class PluginRegistry:
    """
    Central registry for managing Scribe plugins.

    Responsibilities:
    - Discover and load plugins from plugins directory
    - Validate plugins before activation
    - Initialize plugins with configuration
    - Route voice commands to appropriate plugin handlers
    - Manage plugin lifecycle (shutdown, reload)

    Example:
        registry = PluginRegistry()
        registry.load_plugins(config)

        # Execute a command
        result = registry.execute_command("switch to chrome")
    """

    def __init__(self):
        """Initialize empty plugin registry."""
        self._plugins: Dict[str, BasePlugin] = {}
        self._commands: Dict[str, List[RegisteredCommand]] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}

    def register_plugin(self, plugin: BasePlugin, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a plugin instance with the registry.

        Args:
            plugin: Plugin instance to register
            config: Plugin-specific configuration

        Returns:
            True if registration successful, False otherwise

        Raises:
            PluginError: If plugin fails validation or initialization
        """
        # Validate plugin structure
        is_valid, error_msg = plugin.validate()
        if not is_valid:
            logger.error(f"Plugin {plugin.name} failed validation: {error_msg}")
            raise PluginError(f"Plugin validation failed: {error_msg}")

        # Check for duplicate plugin names
        if plugin.name in self._plugins:
            logger.warning(f"Plugin {plugin.name} already registered. Skipping.")
            return False

        # Initialize plugin
        plugin_config = config or {}
        try:
            if not plugin.initialize(plugin_config):
                logger.error(f"Plugin {plugin.name} initialization returned False")
                return False
        except Exception as e:
            logger.error(f"Plugin {plugin.name} initialization failed: {e}")
            raise PluginError(f"Plugin initialization failed: {e}")

        # Register plugin
        self._plugins[plugin.name] = plugin
        self._plugin_configs[plugin.name] = plugin_config

        # Register all commands from this plugin
        try:
            commands = plugin.commands()
            for cmd_def in commands:
                self._register_command(plugin, cmd_def)
        except Exception as e:
            # Rollback registration
            del self._plugins[plugin.name]
            del self._plugin_configs[plugin.name]
            logger.error(f"Failed to register commands for {plugin.name}: {e}")
            raise PluginError(f"Command registration failed: {e}")

        logger.info(f"✅ Registered plugin: {plugin.name} v{plugin.version}")
        return True

    def _register_command(self, plugin: BasePlugin, cmd_def: CommandDefinition):
        """Register individual command patterns with routing information."""
        for pattern in cmd_def.patterns:
            if pattern not in self._commands:
                self._commands[pattern] = []

            registered_cmd = RegisteredCommand(
                plugin=plugin,
                definition=cmd_def,
                pattern=pattern
            )
            self._commands[pattern].append(registered_cmd)
            logger.debug(f"Registered command pattern: '{pattern}' -> {plugin.name}")

    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin and clean up its resources.

        Args:
            plugin_name: Name of plugin to unregister

        Returns:
            True if unregistration successful, False if plugin not found
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Cannot unregister unknown plugin: {plugin_name}")
            return False

        plugin = self._plugins[plugin_name]

        # Shutdown plugin
        try:
            plugin.shutdown()
        except Exception as e:
            logger.error(f"Error during {plugin_name} shutdown: {e}")

        # Remove commands
        patterns_to_remove = []
        for pattern, cmds in self._commands.items():
            self._commands[pattern] = [cmd for cmd in cmds if cmd.plugin.name != plugin_name]
            if not self._commands[pattern]:
                patterns_to_remove.append(pattern)

        for pattern in patterns_to_remove:
            del self._commands[pattern]

        # Remove plugin
        del self._plugins[plugin_name]
        del self._plugin_configs[plugin_name]

        logger.info(f"Unregistered plugin: {plugin_name}")
        return True

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a registered plugin by name."""
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all registered plugins with metadata.

        Returns:
            List of plugin metadata dictionaries
        """
        return [plugin.get_metadata() for plugin in self._plugins.values()]

    def list_commands(self) -> List[Dict[str, Any]]:
        """
        List all registered commands across all plugins.

        Returns:
            List of command information dictionaries
        """
        commands = []
        for pattern, registered_cmds in self._commands.items():
            for reg_cmd in registered_cmds:
                commands.append({
                    "pattern": pattern,
                    "plugin": reg_cmd.plugin.name,
                    "examples": reg_cmd.definition.examples,
                    "description": reg_cmd.definition.description
                })
        return commands

    def find_command(self, pattern: str) -> Optional[List[RegisteredCommand]]:
        """
        Find registered commands matching a pattern.

        Args:
            pattern: Command pattern to search for

        Returns:
            List of matching RegisteredCommand objects, or None if not found
        """
        return self._commands.get(pattern)

    def execute_command(self, pattern: str, **kwargs) -> Any:
        """
        Execute a command by pattern with provided arguments.

        Args:
            pattern: Command pattern to execute
            **kwargs: Arguments to pass to command handler

        Returns:
            Result from command handler

        Raises:
            PluginError: If command not found or execution fails
        """
        commands = self.find_command(pattern)
        if not commands:
            raise PluginError(f"No command registered for pattern: {pattern}")

        # Use first matching command (TODO: Add priority system)
        cmd = commands[0]

        try:
            logger.debug(f"Executing command '{pattern}' via {cmd.plugin.name}")
            return cmd.execute(**kwargs)
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise PluginError(f"Command execution failed: {e}")

    def shutdown_all(self):
        """Shutdown all registered plugins."""
        logger.info("Shutting down all plugins...")
        for plugin_name in list(self._plugins.keys()):
            self.unregister_plugin(plugin_name)
        logger.info("All plugins shutdown complete")

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin (useful for development).

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            True if reload successful, False otherwise
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Cannot reload unknown plugin: {plugin_name}")
            return False

        # Save config
        config = self._plugin_configs.get(plugin_name, {})

        # Get plugin class for re-instantiation
        plugin_class = type(self._plugins[plugin_name])

        # Unregister current instance
        self.unregister_plugin(plugin_name)

        # Create new instance and register
        try:
            new_plugin = plugin_class()
            return self.register_plugin(new_plugin, config)
        except Exception as e:
            logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return False

    @classmethod
    def discover_plugins(cls, plugins_dir: Path) -> List[BasePlugin]:
        """
        Discover plugins in a directory by convention.

        Convention: Each plugin in its own subdirectory with plugin.py
        Example: plugins/window_manager/plugin.py

        Args:
            plugins_dir: Directory to search for plugins

        Returns:
            List of discovered plugin instances

        Note:
            This is a convenience method. For production, use explicit registration.
        """
        discovered = []

        if not plugins_dir.exists():
            logger.warning(f"Plugins directory does not exist: {plugins_dir}")
            return discovered

        for plugin_path in plugins_dir.iterdir():
            if not plugin_path.is_dir():
                continue

            plugin_file = plugin_path / "plugin.py"
            if not plugin_file.exists():
                continue

            try:
                # Load module dynamically
                spec = importlib.util.spec_from_file_location(
                    f"scribe.plugins.{plugin_path.name}",
                    plugin_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find BasePlugin subclasses in module
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if (isinstance(item, type) and
                            issubclass(item, BasePlugin) and
                            item is not BasePlugin):

                            # Instantiate plugin
                            plugin_instance = item()
                            discovered.append(plugin_instance)
                            logger.info(f"Discovered plugin: {plugin_instance.name}")

            except Exception as e:
                logger.error(f"Failed to load plugin from {plugin_path}: {e}")

        return discovered

    def __repr__(self) -> str:
        return f"<PluginRegistry plugins={len(self._plugins)} commands={len(self._commands)}>"
