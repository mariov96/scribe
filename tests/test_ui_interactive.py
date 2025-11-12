"""
Interactive UI Test - Manual verification of UI functionality

This test opens actual UI components for manual interaction testing.
Use this to verify buttons, navigation, and visual elements work correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

from scribe.analytics.value_calculator import ValueCalculator
from scribe.config.config_manager import ConfigManager
from scribe.plugins.registry import PluginRegistry
from scribe.ui_fluent.main_window import ScribeMainWindow


def test_main_window_interactive():
    """
    Interactive test for main window functionality.
    
    Tests:
    1. Window opens and displays correctly
    2. Navigation between pages works
    3. HomePage shows metrics (will be 0 for new session)
    4. InsightsPage shows starter insights
    5. PluginsPage displays correctly
    6. Settings page accessible
    """
    
    print("\n" + "="*60)
    print("INTERACTIVE UI TEST - MAIN WINDOW")
    print("="*60)
    print("\nStarting Scribe Main Window...")
    print("\n📋 Test Checklist:")
    print("  1. Window opens at 1200x800")
    print("  2. Navigation sidebar visible on left")
    print("  3. Click 'Home' - see dashboard with metrics")
    print("  4. Click 'Transcribe' - see transcription controls")
    print("  5. Click 'Plugins' - see plugin list")
    print("  6. Click 'Insights' - see insights cards")
    print("  7. Click 'Settings' at bottom - see settings")
    print("  8. Click 'About' at bottom - see about page")
    print("\n✅ If all pages display correctly, UI is functional!")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    # Create temporary config
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    config_dir = temp_dir / "config"
    config_dir.mkdir()
    
    # Setup components
    config_manager = ConfigManager(config_dir / "test_config.yaml")
    plugin_registry = PluginRegistry()
    value_calculator = ValueCalculator()
    
    # Add some sample data so HomePage shows something
    value_calculator.record_transcription(
        audio_duration=5.0,
        word_count=100,
        transcription_time=1.5,
        corrections_made=2
    )
    
    value_calculator.record_command("test command", "test_plugin", 0.3, True)
    
    # Create and show main window
    window = ScribeMainWindow(config_manager, plugin_registry, value_calculator)
    window.show()
    
    # Show instructions after window appears
    def show_instructions():
        msg = QMessageBox(window)
        msg.setWindowTitle("Interactive UI Test")
        msg.setText("Test the UI by clicking through all pages in the sidebar.")
        msg.setInformativeText(
            "Check that:\n"
            "• All pages display correctly\n"
            "• HomePage shows 100 words, 1 command\n"
            "• InsightsPage shows insights\n"
            "• PluginsPage shows sample plugins\n"
            "• Navigation works smoothly\n\n"
            "Close this window when done testing."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    QTimer.singleShot(500, show_instructions)
    
    result = app.exec()
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    
    return result


def test_individual_pages():
    """Quick test of individual pages in separate windows"""
    
    print("\n" + "="*60)
    print("INDIVIDUAL PAGE TESTS")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    from scribe.ui_fluent.pages.home import HomePage
    from scribe.ui_fluent.pages.insights import InsightsPage
    from scribe.ui_fluent.pages.plugins import PluginsPage
    
    # Create calculator with data
    calc = ValueCalculator()
    calc.record_transcription(5.0, 100, 1.5, 0.3, 2)
    calc.record_command("test", "test_plugin", 0.2, True)
    
    # Test HomePage
    print("\n📄 Testing HomePage...")
    home = HomePage(calc)
    home.setWindowTitle("Test: HomePage")
    home.resize(900, 700)
    home.show()
    
    # Test InsightsPage  
    print("📊 Testing InsightsPage...")
    insights = InsightsPage(calc)
    insights.setWindowTitle("Test: InsightsPage")
    insights.resize(900, 700)
    insights.move(920, 0)
    insights.show()
    
    # Test PluginsPage
    print("🔌 Testing PluginsPage...")
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    config_dir = temp_dir / "config"
    config_dir.mkdir()
    
    config_manager = ConfigManager(config_dir / "test_config.yaml")
    plugin_registry = PluginRegistry()
    
    plugins = PluginsPage(plugin_registry, config_manager)
    plugins.setWindowTitle("Test: PluginsPage")
    plugins.resize(900, 700)
    plugins.move(0, 720)
    plugins.show()
    
    print("\n✅ All pages opened. Check that content displays correctly.")
    print("   Close any window to end test.")
    
    result = app.exec()
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    
    return result


if __name__ == "__main__":
    import sys
    
    print("\n🧪 SCRIBE INTERACTIVE UI TESTS")
    print("\nChoose test:")
    print("1. Main Window (full integration)")
    print("2. Individual Pages (side-by-side)")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        sys.exit(test_main_window_interactive())
    elif choice == "2":
        sys.exit(test_individual_pages())
    elif choice == "3":
        test_individual_pages()
        test_main_window_interactive()
    else:
        print("Invalid choice")
        sys.exit(1)
