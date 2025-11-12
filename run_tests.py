"""
Simple test runner to validate our implementations
"""
import sys
sys.path.insert(0, "src")

print("=" * 60)
print("SCRIBE TEST SUITE")
print("=" * 60)
print()

# Test 1: Pattern Matching
print("TEST 1: Pattern Matching with Variable Extraction")
print("-" * 60)

from test_pattern_matching import pattern_matches

test_cases = [
    ("switch to chrome", "switch to {app}", True, {"app": "chrome"}),
    ("switch to visual studio code", "switch to {app}", True, {"app": "visual studio code"}),
    ("open spotify", "open {app}", True, {"app": "spotify"}),
    ("minimize", "minimize", True, {}),
    ("close firefox now", "close {app}", True, {"app": "firefox now"}),
    ("open file.txt in notepad", "open {file} in {app}", True, {"file": "file.txt", "app": "notepad"}),
]

passed = 0
failed = 0

for text, pattern, expected_match, expected_params in test_cases:
    matched, params = pattern_matches(text, pattern)
    if matched == expected_match and params == expected_params:
        print(f"  ✅ '{text}' vs '{pattern}'")
        passed += 1
    else:
        print(f"  ❌ '{text}' vs '{pattern}'")
        print(f"     Expected: {expected_match}, {expected_params}")
        print(f"     Got: {matched}, {params}")
        failed += 1

print(f"\nPattern Matching: {passed} passed, {failed} failed")
print()

# Test 2: Plugin Registry
print("TEST 2: Plugin Registry")
print("-" * 60)

try:
    from scribe.plugins.registry import PluginRegistry
    from scribe.plugins.base import BasePlugin, CommandDefinition
    
    class TestPlugin(BasePlugin):
        name = "test_plugin"
        version = "1.0.0"
        
        def __init__(self):
            self.initialized = False
            self.called_count = 0
        
        def commands(self):
            return [
                CommandDefinition(
                    patterns=["test command"],
                    handler=self.handle_test,
                    examples=["test command"],
                    description="Test"
                )
            ]
        
        def initialize(self, config):
            self.initialized = True
            return True
        
        def handle_test(self):
            self.called_count += 1
            return "success"
    
    registry = PluginRegistry()
    plugin = TestPlugin()
    
    # Test registration
    result = registry.register_plugin(plugin)
    if result and plugin.initialized:
        print("  ✅ Plugin registration and initialization")
        passed += 1
    else:
        print("  ❌ Plugin registration failed")
        failed += 1
    
    # Test command registration
    if "test command" in registry._commands:
        print("  ✅ Command registration")
        passed += 1
    else:
        print("  ❌ Command registration failed")
        failed += 1
    
    # Test command execution
    commands = registry._commands.get("test command")
    if commands:
        result = commands[0].execute()
        if plugin.called_count == 1 and result == "success":
            print("  ✅ Command execution")
            passed += 1
        else:
            print("  ❌ Command execution failed")
            failed += 1
    
    print(f"\nPlugin Registry: Tests completed")
    
except Exception as e:
    print(f"  ❌ Plugin Registry tests failed with error: {e}")
    failed += 3

print()

# Test 3: History Page (basic)
print("TEST 3: History Page (Basic Structure)")
print("-" * 60)

try:
    from scribe.ui_fluent.pages.history import HistoryPage
    from datetime import datetime
    
    # Just test that it can be imported and basic structure
    print("  ✅ History Page import successful")
    passed += 1
    
    # Check key methods exist
    required_methods = ['add_transcription', 'clear_history', 'get_history', 'load_history']
    page_methods = dir(HistoryPage)
    
    all_present = all(method in page_methods for method in required_methods)
    if all_present:
        print("  ✅ All required methods present")
        passed += 1
    else:
        print("  ❌ Missing required methods")
        failed += 1
    
except Exception as e:
    print(f"  ❌ History Page tests failed: {e}")
    failed += 2

print()
print("=" * 60)
print(f"TOTAL RESULTS: {passed} passed, {failed} failed")
print("=" * 60)

# Exit with appropriate code
sys.exit(0 if failed == 0 else 1)
