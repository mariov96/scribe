"""
Scribe Plugin System

The plugin system allows infinite extensibility while maintaining
a stable core. All new features should be plugins.
"""

from .base import BasePlugin, CommandDefinition, PluginError
from .registry import PluginRegistry

__all__ = [
    "BasePlugin",
    "CommandDefinition",
    "PluginError",
    "PluginRegistry",
]
