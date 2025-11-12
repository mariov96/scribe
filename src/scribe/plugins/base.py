"""
Base Plugin Architecture for Scribe

This module defines the abstract base class that all plugins must inherit from.
Design chosen: Class-Based Inheritance (see docs/PLUGIN_ARCHITECTURES.md)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Any, Optional
from dataclasses import dataclass


@dataclass
class CommandDefinition:
    """
    Definition of a voice command handled by a plugin.

    Attributes:
        patterns: List of command patterns (e.g., ["switch to {app}", "open {app}"])
        handler: Function to call when command matches
        examples: Example commands for help/documentation
        description: Human-readable description of what command does
    """
    patterns: List[str]
    handler: Callable
    examples: List[str]
    description: str = ""


class PluginError(Exception):
    """Base exception for plugin-related errors."""
    pass


class BasePlugin(ABC):
    """
    Abstract base class for all Scribe plugins.

    All plugins must inherit from this class and implement the abstract methods.
    This ensures type safety, clear contracts, and excellent IDE support.

    Design Philosophy:
    - Explicit over implicit
    - Type-safe at import time
    - Performance critical (<100ms command execution)
    - New contributor friendly

    Example:
        class WindowManager(BasePlugin):
            name = "window_manager"
            version = "1.0.0"

            def commands(self):
                return [
                    CommandDefinition(
                        patterns=["switch to {app}"],
                        handler=self.switch_app,
                        examples=["switch to chrome"],
                        description="Switch to specified application"
                    )
                ]

            def initialize(self, config):
                self.config = config
                return True

            def switch_app(self, app: str):
                # Implementation here
                return f"Switched to {app}"
    """

    # Class-level metadata (can be overridden by instances)
    name: str = "unnamed_plugin"
    version: str = "0.0.0"
    description: str = ""
    author: str = ""
    api_version: str = "2.0"  # Scribe API version this plugin targets

    @abstractmethod
    def commands(self) -> List[CommandDefinition]:
        """
        Return list of commands this plugin handles.

        Returns:
            List of CommandDefinition objects

        Example:
            return [
                CommandDefinition(
                    patterns=["do {action}", "perform {action}"],
                    handler=self.do_action,
                    examples=["do something"],
                    description="Perform an action"
                )
            ]
        """
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with configuration.

        Called once when plugin is loaded. Use this to:
        - Store configuration
        - Set up resources
        - Validate requirements
        - Connect to external services

        Args:
            config: Plugin-specific configuration dictionary

        Returns:
            True if initialization successful, False otherwise

        Example:
            def initialize(self, config):
                self.api_key = config.get('api_key')
                if not self.api_key:
                    return False
                return True
        """
        pass

    def shutdown(self):
        """
        Clean up when plugin is unloaded.

        Optional: Override this to clean up resources when plugin stops.
        Called when:
        - User disables plugin
        - Application is closing
        - Plugin is being reloaded

        Example:
            def shutdown(self):
                self.close_connections()
                self.save_state()
        """
        pass

    def validate(self) -> tuple[bool, str]:
        """
        Validate plugin configuration and requirements.

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            def validate(self):
                if not self.has_required_library():
                    return False, "Missing required library: pygetwindow"
                return True, ""
        """
        # Default: Check API version compatibility
        if self.api_version != "2.0":
            return False, f"Plugin API version {self.api_version} not compatible with Scribe 2.0"

        # Check commands are properly defined
        try:
            cmds = self.commands()
            if not isinstance(cmds, list):
                return False, "commands() must return a list"

            for cmd in cmds:
                if not isinstance(cmd, CommandDefinition):
                    return False, f"Invalid command definition: {cmd}"

                if not cmd.patterns:
                    return False, "Command must have at least one pattern"

                if not callable(cmd.handler):
                    return False, f"Command handler must be callable: {cmd.handler}"

        except Exception as e:
            return False, f"Error validating commands: {e}"

        return True, ""

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return plugin metadata.

        Returns:
            Dictionary with plugin information
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "api_version": self.api_version,
            "commands": [
                {
                    "patterns": cmd.patterns,
                    "examples": cmd.examples,
                    "description": cmd.description
                }
                for cmd in self.commands()
            ]
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} version={self.version}>"
