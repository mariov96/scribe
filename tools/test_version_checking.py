#!/usr/bin/env python3
"""
Test script for build timestamp and version checking.

This simulates different scenarios to verify the single instance manager works correctly.
"""

import sys
import time
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scribe.core.single_instance import SingleInstanceManager


def test_scenario(scenario_name, current_version, current_build, new_version, new_build, expected_result):
    """Test a specific scenario."""
    print(f"\n{'='*70}")
    print(f"Scenario: {scenario_name}")
    print(f"{'='*70}")
    print(f"Current instance: v{current_version} (build {current_build})")
    print(f"New instance:     v{new_version} (build {new_build})")
    print(f"Expected:         {expected_result}")
    print()
    
    # Create a mock lock file
    lock_file = Path(tempfile.gettempdir()) / ".scribe_test.lock"
    
    # Write mock current instance
    lock_file.write_text(f"99999|{current_version}|{current_build}")
    
    # Try to acquire with new instance
    manager = SingleInstanceManager("scribe_test", new_version, new_build)
    
    # Override is_process_running to always return True (simulating running process)
    original_check = manager._is_process_running
    manager._is_process_running = lambda pid: True
    
    result = manager.acquire()
    
    # Restore and cleanup
    manager._is_process_running = original_check
    if lock_file.exists():
        lock_file.unlink()
    
    if result:
        print("✅ Result: Acquired (would start new instance)")
    else:
        print("❌ Result: Denied (would show warning)")
    
    return result


def main():
    """Run all test scenarios."""
    print("="*70)
    print("Build Timestamp & Version Checking Test Suite")
    print("="*70)
    
    # Test scenarios
    scenarios = [
        # (name, current_v, current_build, new_v, new_build, should_acquire)
        ("Newer version (any build)", "2.0.0", 1000, "2.0.1", 1000, True),
        ("Older version (any build)", "2.0.1", 1000, "2.0.0", 1000, False),
        ("Same version, newer build", "2.0.1", 1000, "2.0.1", 2000, True),
        ("Same version, older build", "2.0.1", 2000, "2.0.1", 1000, False),
        ("Same version and build", "2.0.1", 1000, "2.0.1", 1000, False),
    ]
    
    results = []
    for scenario in scenarios:
        result = test_scenario(*scenario)
        results.append((scenario[0], result, scenario[5]))
    
    # Summary
    print(f"\n{'='*70}")
    print("Test Summary")
    print(f"{'='*70}")
    
    passed = sum(1 for _, result, expected in results if result == expected)
    total = len(results)
    
    for name, result, expected in results:
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
