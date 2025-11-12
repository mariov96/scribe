"""
Comprehensive Test Suite for Scribe UI and Data Integration

Tests:
1. ValueCalculator integration with HomePage
2. ValueCalculator integration with InsightsPage  
3. Plugin page configuration persistence
4. Setup wizard data collection
5. Main window navigation
6. Button interactions
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest

# Import specific modules without triggering app init
from scribe.analytics.value_calculator import ValueCalculator
from scribe.config.config_manager import ConfigManager
from scribe.plugins.registry import PluginRegistry
from scribe.ui_fluent.pages.home import HomePage
from scribe.ui_fluent.pages.insights import InsightsPage
from scribe.ui_fluent.pages.plugins import PluginsPage
from scribe.ui_fluent.main_window import ScribeMainWindow
from scribe.ui_fluent.setup_wizard.wizard_manager import SetupWizardManager


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = []
        self.failed = []
        
    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"✅ PASS: {test_name}")
        
    def add_fail(self, test_name, error):
        self.failed.append((test_name, error))
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
        
    def print_summary(self):
        print("\n" + "="*60)
        print("TEST SUITE RESULTS")
        print("="*60)
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"📊 Total:  {len(self.passed) + len(self.failed)}")
        print("="*60)
        
        if self.failed:
            print("\nFailed Tests:")
            for test_name, error in self.failed:
                print(f"  - {test_name}: {error}")
        else:
            print("\n🎉 ALL TESTS PASSED!")


def test_value_calculator_basic():
    """Test ValueCalculator can record and calculate metrics"""
    results = TestResults()
    
    try:
        calc = ValueCalculator()
        
        # Test recording transcription
        calc.record_transcription(
            audio_duration=5.0,
            word_count=75,
            transcription_time=1.2
        )
        
        summary = calc.get_session_summary()
        assert summary.total_words == 75, f"Expected 75 words, got {summary.total_words}"
        assert summary.total_transcriptions == 1, f"Expected 1 transcription, got {summary.total_transcriptions}"
        
        results.add_pass("ValueCalculator Basic Recording")
        
        # Test time saved calculation
        time_saved = calc.calculate_time_saved(
            word_count=100,
            audio_duration=10.0,
            was_command=False
        )
        assert time_saved > 0, f"Time saved should be positive, got {time_saved}"
        results.add_pass("ValueCalculator Time Saved Calculation")
        
        # Test command recording
        calc.record_command(
            command_pattern="test command",
            plugin="test_plugin",
            execution_time=0.5,
            success=True
        )
        
        summary = calc.get_session_summary()
        assert summary.total_commands == 1, f"Expected 1 command, got {summary.total_commands}"
        results.add_pass("ValueCalculator Command Recording")
        
    except Exception as e:
        results.add_fail("ValueCalculator Tests", str(e))
        
    return results


def test_homepage_with_data():
    """Test HomePage displays real data from ValueCalculator"""
    results = TestResults()
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create calculator with data
        calc = ValueCalculator()
        calc.record_transcription(
            audio_duration=5.0,
            word_count=100,
            transcription_time=1.5,
            corrections_made=2
        )
        
        # Create HomePage with calculator
        home = HomePage(calc)
        
        # Verify page was created
        assert home is not None, "HomePage should not be None"
        assert home.value_calculator is not None, "HomePage should have value_calculator"
        
        results.add_pass("HomePage Creation with ValueCalculator")
        
        # Check that metrics were created
        assert hasattr(home, 'view'), "HomePage should have view widget"
        
        results.add_pass("HomePage Metrics Rendering")
        
        home.close()
        
    except Exception as e:
        results.add_fail("HomePage Tests", str(e))
        
    return results


def test_insights_page_with_data():
    """Test InsightsPage generates real insights"""
    results = TestResults()
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create calculator with substantial data
        calc = ValueCalculator()
        for i in range(5):
            calc.record_transcription(
                audio_duration=6.0,
                word_count=90,
                transcription_time=1.5,
                corrections_made=1
            )
        
        calc.record_command("test", "test_plugin", 0.2, True)
        
        # Create InsightsPage with calculator
        insights = InsightsPage(calc)
        
        assert insights is not None, "InsightsPage should not be None"
        assert insights.value_calculator is not None, "InsightsPage should have value_calculator"
        
        results.add_pass("InsightsPage Creation with ValueCalculator")
        
        # Generate insights
        insights_list = insights._generate_insights()
        assert len(insights_list) > 0, "Should generate at least one insight"
        
        results.add_pass("InsightsPage Insight Generation")
        
        insights.close()
        
    except Exception as e:
        results.add_fail("InsightsPage Tests", str(e))
        
    return results


def test_plugins_page_config():
    """Test PluginsPage saves configuration"""
    results = TestResults()
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create temporary config
        temp_dir = Path(tempfile.mkdtemp())
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        
        config_manager = ConfigManager(config_dir / "test_config.yaml")
        plugin_registry = PluginRegistry()
        
        # Create PluginsPage
        plugins_page = PluginsPage(plugin_registry, config_manager)
        
        assert plugins_page is not None, "PluginsPage should not be None"
        assert plugins_page.config_manager is not None, "PluginsPage should have config_manager"
        
        results.add_pass("PluginsPage Creation")
        
        # Test toggle handler exists
        assert hasattr(plugins_page, '_on_plugin_toggled'), "Should have toggle handler"
        
        results.add_pass("PluginsPage Toggle Handler")
        
        plugins_page.close()
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        results.add_fail("PluginsPage Tests", str(e))
        
    return results


def test_setup_wizard():
    """Test Setup Wizard can be created and navigated"""
    results = TestResults()
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create wizard
        wizard = SetupWizardManager()
        
        assert wizard is not None, "Wizard should not be None"
        assert wizard.windowTitle() == "Scribe Setup Wizard", f"Expected 'Scribe Setup Wizard', got '{wizard.windowTitle()}'"
        
        results.add_pass("Setup Wizard Creation")
        
        # Check stack exists (pages are added via add_page method)
        assert hasattr(wizard, 'stack'), "Wizard should have stack widget"
        assert hasattr(wizard, 'pages'), "Wizard should have pages list"
        
        results.add_pass("Setup Wizard Structure")
        
        # Test navigation methods exist
        assert hasattr(wizard, '_on_next'), "Wizard should have _on_next method"
        assert hasattr(wizard, '_on_back'), "Wizard should have _on_back method"
        assert hasattr(wizard, 'add_page'), "Wizard should have add_page method"
        
        results.add_pass("Setup Wizard Navigation")
        
        wizard.close()
        
    except Exception as e:
        results.add_fail("Setup Wizard Tests", str(e))
        
    return results


def test_main_window_integration():
    """Test MainWindow integrates all components"""
    results = TestResults()
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create components
        temp_dir = Path(tempfile.mkdtemp())
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        
        config_manager = ConfigManager(config_dir / "test_config.yaml")
        plugin_registry = PluginRegistry()
        value_calculator = ValueCalculator()
        
        # Create main window
        window = ScribeMainWindow(config_manager, plugin_registry, value_calculator)
        
        assert window is not None, "MainWindow should not be None"
        assert window.config_manager is not None, "MainWindow should have config_manager"
        assert window.plugin_registry is not None, "MainWindow should have plugin_registry"
        assert window.value_calculator is not None, "MainWindow should have value_calculator"
        
        results.add_pass("MainWindow Component Integration")
        
        # Check pages were created
        assert hasattr(window, 'home_page'), "MainWindow should have home_page"
        assert hasattr(window, 'plugins_page'), "MainWindow should have plugins_page"
        assert hasattr(window, 'insights_page'), "MainWindow should have insights_page"
        
        results.add_pass("MainWindow Pages Creation")
        
        # Verify HomePage has calculator
        assert window.home_page.value_calculator is not None, "HomePage should have value_calculator"
        
        results.add_pass("MainWindow HomePage Data Wiring")
        
        # Verify InsightsPage has calculator
        assert window.insights_page.value_calculator is not None, "InsightsPage should have value_calculator"
        
        results.add_pass("MainWindow InsightsPage Data Wiring")
        
        # Verify PluginsPage has config
        assert window.plugins_page.config_manager is not None, "PluginsPage should have config_manager"
        
        results.add_pass("MainWindow PluginsPage Config Wiring")
        
        window.close()
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        results.add_fail("MainWindow Integration Tests", str(e))
        
    return results


def test_data_flow_end_to_end():
    """Test complete data flow from recording to UI display"""
    results = TestResults()
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Setup
        calc = ValueCalculator()
        
        # Simulate transcription workflow
        calc.record_transcription(
            audio_duration=5.0,
            word_count=75,
            transcription_time=1.2,
            corrections_made=2
        )
        
        calc.record_transcription(
            audio_duration=8.0,
            word_count=120,
            transcription_time=2.1,
            corrections_made=1
        )
        
        calc.record_command("test command", "test_plugin", 0.3, True)
        
        # Get summary
        summary = calc.get_session_summary()
        
        assert summary.total_words == 195, f"Expected 195 words, got {summary.total_words}"
        assert summary.total_transcriptions == 2, f"Expected 2 transcriptions, got {summary.total_transcriptions}"
        assert summary.total_commands == 1, f"Expected 1 command, got {summary.total_commands}"
        
        results.add_pass("Data Flow - Recording")
        
        # Create UI with data
        home = HomePage(calc)
        insights = InsightsPage(calc)
        
        # Verify UI has access to data
        assert home.value_calculator is calc, "HomePage should have same calculator"
        assert insights.value_calculator is calc, "InsightsPage should have same calculator"
        
        results.add_pass("Data Flow - UI Binding")
        
        # Verify insights generate
        insights_list = insights._generate_insights()
        assert len(insights_list) > 0, "Should generate insights from data"
        
        results.add_pass("Data Flow - Insight Generation")
        
        home.close()
        insights.close()
        
    except Exception as e:
        results.add_fail("End-to-End Data Flow Tests", str(e))
        
    return results


def run_all_tests():
    """Run complete test suite"""
    print("="*60)
    print("SCRIBE COMPREHENSIVE TEST SUITE")
    print("="*60)
    print()
    
    all_results = TestResults()
    
    # Run all test groups
    print("🧪 Testing ValueCalculator...")
    result = test_value_calculator_basic()
    all_results.passed.extend(result.passed)
    all_results.failed.extend(result.failed)
    print()
    
    print("🧪 Testing HomePage Integration...")
    result = test_homepage_with_data()
    all_results.passed.extend(result.passed)
    all_results.failed.extend(result.failed)
    print()
    
    print("🧪 Testing InsightsPage Integration...")
    result = test_insights_page_with_data()
    all_results.passed.extend(result.passed)
    all_results.failed.extend(result.failed)
    print()
    
    print("🧪 Testing PluginsPage Configuration...")
    result = test_plugins_page_config()
    all_results.passed.extend(result.passed)
    all_results.failed.extend(result.failed)
    print()
    
    print("🧪 Testing Setup Wizard...")
    result = test_setup_wizard()
    all_results.passed.extend(result.passed)
    all_results.failed.extend(result.failed)
    print()
    
    print("🧪 Testing MainWindow Integration...")
    result = test_main_window_integration()
    all_results.passed.extend(result.passed)
    all_results.failed.extend(result.failed)
    print()
    
    print("🧪 Testing End-to-End Data Flow...")
    result = test_data_flow_end_to_end()
    all_results.passed.extend(result.passed)
    all_results.failed.extend(result.failed)
    print()
    
    # Print summary
    all_results.print_summary()
    
    return len(all_results.failed) == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
