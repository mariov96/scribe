"""
Scribe Configuration Management.
"""

from .config_manager import ConfigManager
from .models import (
    ScribeConfig as AppConfig,
    AudioConfig,
    HotkeyConfig,
    WhisperConfig,
    AIFormattingConfig,
    PostProcessingConfig,
    PluginConfig,
    UIConfig
)

__all__ = [
    "ConfigManager",
    "ScribeConfig",
    "AudioConfig",
    "HotkeyConfig",
    "WhisperConfig",
    "AIFormattingConfig",
    "PostProcessingConfig",
    "PluginConfig",
    "UIConfig"
]
