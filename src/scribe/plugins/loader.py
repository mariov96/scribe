"""
Plugin Loader for Scribe.

Dynamically discovers and loads plugins from the specified plugin directories.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import List

from .base import BasePlugin

logger = logging.getLogger(__name__)

def load_plugins(plugin_dirs: List[Path]) -> List[BasePlugin]:
    """
    Discover and load all valid plugins from the given directories.

    Args:
        plugin_dirs: A list of directories to search for plugins.

    Returns:
        A list of instantiated plugin objects.
    """
    loaded_plugins = []
    for plugin_dir in plugin_dirs:
        if not plugin_dir.is_dir():
            continue

        for module_path in plugin_dir.glob("*/plugin.py"):
            try:
                # Derive module name from path (e.g., scribe.plugins.community.example.plugin)
                # Derive module name from path (e.g., scribe.plugins.community.example.plugin)
                relative_path = module_path.relative_to(Path.cwd())
                module_name = str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")
                # remove src from module name
                module_name = module_name.replace("src.", "")

                module = importlib.import_module(module_name)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                        plugin_instance = obj()
                        loaded_plugins.append(plugin_instance)
                        logger.info(f"Successfully loaded plugin: {plugin_instance.name}")
                        break # Load only one plugin per plugin.py
            except Exception as e:
                logger.error(f"Failed to load plugin from {module_path}: {e}", exc_info=True)

    return loaded_plugins