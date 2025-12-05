"""
Visual Verification Script for Scribe UI Redesign
This script launches the modernized pages individually for visual inspection.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from qfluentwidgets import setTheme, Theme, setThemeColor

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scribe.ui_fluent.pages.home import HomePage
from scribe.ui_fluent.pages.transcription import TranscriptionPage
from scribe.ui_fluent.pages.settings import SettingsPage
from scribe.ui_fluent.pages.insights import InsightsPage
from scribe.ui_fluent.pages.plugins import PluginsPage
from scribe.config import ConfigManager
from scribe.analytics.value_calculator import ValueCalculator

class VerificationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scribe UI Redesign Verification")
        self.resize(1200, 800)
        
        # Setup theme
        setTheme(Theme.DARK)
        setThemeColor("#6751A1")
        
        # Mock dependencies
        self.config_manager = ConfigManager()
        self.value_calculator = ValueCalculator()
        
        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Tabs for each page
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # 1. Home Page
        self.home_page = HomePage(self.value_calculator)
        self.tabs.addTab(self.home_page, "🏠 Home")
        
        # 2. Transcription Page
        self.transcription_page = TranscriptionPage(self.config_manager)
        self.tabs.addTab(self.transcription_page, "🎤 Transcription")
        
        # 3. Settings Page
        self.settings_page = SettingsPage(self.config_manager)
        self.tabs.addTab(self.settings_page, "⚙️ Settings")
        
        # 4. Insights Page
        self.insights_page = InsightsPage(self.value_calculator)
        self.tabs.addTab(self.insights_page, "📊 Insights")
        
        # 5. Plugins Page
        self.plugins_page = PluginsPage(None, self.config_manager)
        self.tabs.addTab(self.plugins_page, "🧩 Plugins")
        
        # Simulate some data
        self._simulate_data()
        
    def _simulate_data(self):
        # Update Home stats
        self.home_page.update_stats(
            total_transcriptions=12,
            words_saved=4500,
            time_saved_seconds=6750
        )
        
        # Update Transcription metrics
        self.transcription_page.update_metrics(
            words=125,
            duration=45.5,
            confidence=0.98
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VerificationWindow()
    window.show()
    print("\n✨ UI Verification Window Launched")
    print("Please inspect each tab to verify the redesign.")
    sys.exit(app.exec_())