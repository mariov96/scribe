"""
Setup Wizard for Scribe first-run configuration.

Provides a multi-step wizard to guide new users through:
- Welcome and introduction
- Audio device selection and testing
- Hotkey configuration
- Completion and first launch
"""

from .wizard_manager import SetupWizardManager
from .base_page import BasePage
from .welcome_page import WelcomePage
from .audio_device_page import AudioDevicePage
from .hotkey_config_page import HotkeyConfigPage
from .completion_page import CompletionPage

__all__ = [
    'SetupWizardManager',
    'BasePage',
    'WelcomePage',
    'AudioDevicePage',
    'HotkeyConfigPage',
    'CompletionPage'
]
