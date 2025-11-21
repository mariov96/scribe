"""
Scribe UI Pages
"""

from .home import HomePage
from .transcription import TranscriptionPage
from .plugins import PluginsPage
from .insights import InsightsPage
from .history import HistoryPage
from .settings import SettingsPage
from .about import AboutPage
from .dashboard import DashboardPage
from .home_modern import ModernHomePage

__all__ = [
    'HomePage',
    'TranscriptionPage',
    'PluginsPage',
    'InsightsPage',
    'HistoryPage',
    'SettingsPage',
    'AboutPage',
    'DashboardPage',
    'ModernHomePage'
]
