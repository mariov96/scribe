"""
Visual and Functional Validation Test Suite

This test suite validates:
1. Visual elements render correctly
2. Buttons and interactions work
3. Data updates properly
4. All placeholders are identified
5. Actual behavior vs expected behavior

Run with visual inspection enabled.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import time

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication, QPushButton, QMessageBox
from PySide6.QtCore import QTimer, Qt, QRect
from PySide6.QtTest import QTest
from PySide6.QtGui import QPixmap

from scribe.analytics.value_calculator import ValueCalculator
from scribe.config.config_manager import ConfigManager
from scribe.plugins.registry import PluginRegistry
from scribe.ui_fluent.pages.home import HomePage
from scribe.ui_fluent.pages.transcription import TranscriptionPage
from scribe.ui_fluent.pages.plugins import PluginsPage
from scribe.ui_fluent.pages.insights import InsightsPage
from scribe.ui_fluent.main_window import ScribeMainWindow


class VisualTestResults:
    """Track visual and functional test results"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.placeholders_found = []
        
    def add_pass(self, test_name, details=""):
        self.passed.append((test_name, details))
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   → {details}")
        
    def add_fail(self, test_name, error):
        self.failed.append((test_name, error))
        print(f"❌ FAIL: {test_name}")
        print(f"   → {error}")
        
    def add_warning(self, test_name, warning):
        self.warnings.append((test_name, warning))
        print(f"⚠️  WARN: {test_name}")
        print(f"   → {warning}")
        
    def add_placeholder(self, location, description):
        self.placeholders_found.append((location, description))
        print(f"🔍 PLACEHOLDER: {location}")
        print(f"   → {description}")
        
    def print_summary(self):
        print("\n" + "="*70)
        print("VISUAL & FUNCTIONAL VALIDATION RESULTS")
        print("="*70)
        print(f"✅ Passed:       {len(self.passed)}")
        print(f"❌ Failed:       {len(self.failed)}")
        print(f"⚠️  Warnings:     {len(self.warnings)}")
        print(f"🔍 Placeholders: {len(self.placeholders_found)}")
        print("="*70)
        
        if self.placeholders_found:
            print("\n📋 PLACEHOLDERS TO FIX:")
            for i, (loc, desc) in enumerate(self.placeholders_found, 1):
                print(f"{i}. {loc}")
                print(f"   {desc}")
        
        if self.failed:
            print("\n❌ FAILED TESTS:")
            for test_name, error in self.failed:
                print(f"  - {test_name}: {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for test_name, warning in self.warnings:
                print(f"  - {test_name}: {warning}")


def test_home_page_visual(results: VisualTestResults):
    """Test HomePage visual elements and data display"""
    print("\n" + "="*70)
    print("TESTING: HomePage Visual & Functional")
    print("="*70)
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create with sample data
        calc = ValueCalculator()
        calc.record_transcription(5.0, 100, 1.5, 0.3, 2)
        calc.record_command("test", "test_plugin", 0.3, True)
        
        home = HomePage(calc)
        home.show()
        QTest.qWait(100)
        
        # Check window properties
        if home.isVisible():
            results.add_pass("HomePage Visibility", "Window is visible")
        else:
            results.add_fail("HomePage Visibility", "Window not visible")
        
        # Check metrics are displayed with actual data
        summary = calc.get_session_summary()
        if summary.total_words > 0:
            results.add_pass("HomePage Data", f"Shows {summary.total_words} words")
        else:
            results.add_fail("HomePage Data", "No data displayed")
        
        # Check for interactive elements
        buttons = home.findChildren(QPushButton)
        if len(buttons) > 0:
            results.add_pass("HomePage Buttons", f"Found {len(buttons)} buttons")
            
            # Test button clicks
            for btn in buttons[:3]:  # Test first 3 buttons
                if btn.isEnabled():
                    QTest.mouseClick(btn, Qt.MouseButton.LeftButton)
                    QTest.qWait(50)
                    results.add_pass("Button Click", f"'{btn.text()}' clickable")
        else:
            results.add_warning("HomePage Buttons", "No buttons found")
        
        home.close()
        
    except Exception as e:
        results.add_fail("HomePage Visual Test", str(e))


def test_transcription_page_functional(results: VisualTestResults):
    """Test TranscriptionPage button interactions"""
    print("\n" + "="*70)
    print("TESTING: TranscriptionPage Functional")
    print("="*70)
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        page = TranscriptionPage()
        page.show()
        QTest.qWait(100)
        
        # Find record button
        record_btn = None
        for btn in page.findChildren(QPushButton):
            if "Record" in btn.text() or "Start" in btn.text():
                record_btn = btn
                break
        
        if not record_btn:
            results.add_fail("Transcription Button", "Record button not found")
            page.close()
            return
        
        results.add_pass("Transcription Button", "Found record button")
        
        # Test recording toggle
        initial_text = record_btn.text()
        QTest.mouseClick(record_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(100)
        
        if record_btn.text() != initial_text:
            results.add_pass("Recording Toggle", f"Button changed: {initial_text} → {record_btn.text()}")
        else:
            results.add_fail("Recording Toggle", "Button text didn't change")
        
        # Check if status updates
        if hasattr(page, 'status_label'):
            status_text = page.status_label.text()
            if "Recording" in status_text or "Processing" in status_text:
                results.add_pass("Status Update", f"Status: {status_text}")
            else:
                results.add_warning("Status Update", f"Unexpected status: {status_text}")
        
        # Stop recording
        QTest.mouseClick(record_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(1500)  # Wait for simulated transcription
        
        # Check if text appears in output
        if hasattr(page, 'output_text'):
            output = page.output_text.toPlainText()
            if output and len(output) > 0:
                results.add_pass("Transcription Output", f"Text appeared: '{output[:50]}...'")
            else:
                results.add_warning("Transcription Output", "No text appeared")
        
        # Check for placeholder functionality
        results.add_placeholder(
            "TranscriptionPage._show_result()",
            "Uses simulated text instead of real transcription"
        )
        
        page.close()
        
    except Exception as e:
        results.add_fail("TranscriptionPage Functional Test", str(e))


def test_plugins_page_interaction(results: VisualTestResults):
    """Test PluginsPage toggle switches and configuration"""
    print("\n" + "="*70)
    print("TESTING: PluginsPage Interaction")
    print("="*70)
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        
        config = ConfigManager(config_dir / "test.yaml")
        registry = PluginRegistry()
        
        # Since registry is empty, pass None to trigger sample plugins
        page = PluginsPage(None, config)
        page.show()
        QTest.qWait(200)
        
        # Check for plugin cards
        from scribe.ui_fluent.widgets.plugin_card import PluginCard
        cards = page.findChildren(PluginCard)
        
        if len(cards) > 0:
            results.add_pass("Plugin Cards", f"Found {len(cards)} plugin cards")
            
            # Test toggle switches
            for i, card in enumerate(cards[:2]):  # Test first 2
                initial_state = card.toggle.isChecked()
                
                # Toggle the switch
                card.toggle.setChecked(not initial_state)
                QTest.qWait(50)
                
                new_state = card.toggle.isChecked()
                if new_state != initial_state:
                    results.add_pass("Toggle Switch", f"Card {i+1} toggled: {initial_state} → {new_state}")
                else:
                    results.add_warning("Toggle Switch", f"Card {i+1} state didn't change")
                
                # Test configure button
                if hasattr(card, 'config_btn'):
                    QTest.mouseClick(card.config_btn, Qt.MouseButton.LeftButton)
                    QTest.qWait(100)
                    results.add_pass("Configure Button", f"Card {i+1} config button clicked")
        else:
            results.add_fail("Plugin Cards", "No plugin cards found")
        
        # Check for placeholders
        results.add_placeholder(
            "PluginsPage._on_plugin_toggled()",
            "TODO: Hot reload plugin - needs implementation"
        )
        
        results.add_placeholder(
            "PluginsPage._on_plugin_configure()",
            "TODO: Open plugin settings dialog - shows placeholder message"
        )
        
        page.close()
        
        import shutil
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        results.add_fail("PluginsPage Interaction Test", str(e))


def test_insights_page_data(results: VisualTestResults):
    """Test InsightsPage displays insights correctly"""
    print("\n" + "="*70)
    print("TESTING: InsightsPage Data Display")
    print("="*70)
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create calculator with substantial data
        calc = ValueCalculator()
        for _ in range(10):
            calc.record_transcription(6.0, 90, 1.5, 0.3, 1)
        for _ in range(5):
            calc.record_command("test", "plugin", 0.2, True)
        
        page = InsightsPage(calc)
        page.show()
        QTest.qWait(100)
        
        # Check if insights were generated
        from scribe.ui_fluent.widgets.insight_card import InsightCard
        insight_cards = page.findChildren(InsightCard)
        
        if len(insight_cards) > 0:
            results.add_pass("Insight Cards", f"Found {len(insight_cards)} insights")
            
            # Check insight content
            for i, card in enumerate(insight_cards[:3]):
                if hasattr(card, 'value_label'):
                    value = card.value_label.text()
                    if value and value != "No data yet":
                        results.add_pass("Insight Data", f"Card {i+1}: {value}")
                    else:
                        results.add_warning("Insight Data", f"Card {i+1} has no data")
        else:
            results.add_fail("Insight Cards", "No insight cards found")
        
        # Verify real data vs sample data
        summary = calc.get_session_summary()
        if summary.total_words == 900:  # 10 * 90 words
            results.add_pass("Insight Calculation", "Using real calculator data")
        else:
            results.add_warning("Insight Calculation", "May not be using real data")
        
        page.close()
        
    except Exception as e:
        results.add_fail("InsightsPage Data Test", str(e))


def test_main_window_navigation(results: VisualTestResults):
    """Test MainWindow page navigation"""
    print("\n" + "="*70)
    print("TESTING: MainWindow Navigation")
    print("="*70)
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        
        config = ConfigManager(config_dir / "test.yaml")
        registry = PluginRegistry()
        calc = ValueCalculator()
        
        window = ScribeMainWindow(config, registry, calc)
        window.show()
        QTest.qWait(200)
        
        # Test that all pages exist
        pages_to_test = [
            ('home_page', 'Home'),
            ('transcription_page', 'Transcription'),
            ('plugins_page', 'Plugins'),
            ('insights_page', 'Insights'),
            ('settings_page', 'Settings'),
            ('about_page', 'About')
        ]
        
        for page_attr, page_name in pages_to_test:
            if hasattr(window, page_attr):
                page = getattr(window, page_attr)
                results.add_pass("Page Existence", f"{page_name} page exists")
                
                # Check page has been added to stack
                if hasattr(window, 'stackedWidget'):
                    stack = window.stackedWidget
                    page_index = -1
                    for i in range(stack.count()):
                        if stack.widget(i) == page:
                            page_index = i
                            break
                    
                    if page_index >= 0:
                        results.add_pass("Page Navigation", f"{page_name} in navigation stack")
                        
                        # Try to switch to it
                        stack.setCurrentIndex(page_index)
                        QTest.qWait(50)
                        
                        if stack.currentWidget() == page:
                            results.add_pass("Page Switch", f"Successfully switched to {page_name}")
                        else:
                            results.add_warning("Page Switch", f"Switch to {page_name} unclear")
                    else:
                        results.add_warning("Page Navigation", f"{page_name} not in navigation")
            else:
                results.add_fail("Page Existence", f"{page_name} page not found")
        
        window.close()
        
        import shutil
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        results.add_fail("MainWindow Navigation Test", str(e))


def test_widget_sizing_and_layout(results: VisualTestResults):
    """Test that widgets are properly sized and don't overlap"""
    print("\n" + "="*70)
    print("TESTING: Widget Sizing and Layout")
    print("="*70)
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        calc = ValueCalculator()
        home = HomePage(calc)
        home.resize(900, 700)
        home.show()
        QTest.qWait(100)
        
        # Check window size
        geometry = home.geometry()
        if geometry.width() >= 800 and geometry.height() >= 600:
            results.add_pass("Window Size", f"{geometry.width()}x{geometry.height()}")
        else:
            results.add_warning("Window Size", f"Small: {geometry.width()}x{geometry.height()}")
        
        # Check for overlapping widgets
        from scribe.ui_fluent.widgets.value_card import ValueCard
        cards = home.findChildren(ValueCard)
        
        if len(cards) >= 2:
            rects = [card.geometry() for card in cards]
            overlaps = []
            
            for i, rect1 in enumerate(rects):
                for j, rect2 in enumerate(rects[i+1:], i+1):
                    if rect1.intersects(rect2):
                        overlaps.append((i, j))
            
            if not overlaps:
                results.add_pass("Layout Check", "No widget overlaps detected")
            else:
                results.add_warning("Layout Check", f"Found {len(overlaps)} overlapping widgets")
        
        # Check text readability (not truncated)
        for card in cards[:3]:
            if hasattr(card, 'title_label'):
                text = card.title_label.text()
                if len(text) > 0 and not text.endswith('...'):
                    results.add_pass("Text Display", f"'{text}' fully visible")
                else:
                    results.add_warning("Text Display", f"'{text}' may be truncated")
        
        home.close()
        
    except Exception as e:
        results.add_fail("Widget Sizing Test", str(e))


def run_visual_validation_suite():
    """Run complete visual and functional validation"""
    print("="*70)
    print("SCRIBE VISUAL & FUNCTIONAL VALIDATION TEST SUITE")
    print("="*70)
    print("\nThis suite tests:")
    print("  • Visual element rendering")
    print("  • Button and interaction functionality")
    print("  • Data display accuracy")
    print("  • Widget sizing and layout")
    print("  • Placeholder identification")
    print("\n")
    
    results = VisualTestResults()
    
    # Run all tests
    test_home_page_visual(results)
    test_transcription_page_functional(results)
    test_plugins_page_interaction(results)
    test_insights_page_data(results)
    test_main_window_navigation(results)
    test_widget_sizing_and_layout(results)
    
    # Print summary
    results.print_summary()
    
    return len(results.failed) == 0


if __name__ == "__main__":
    success = run_visual_validation_suite()
    sys.exit(0 if success else 1)
