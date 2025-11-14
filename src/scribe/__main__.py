"""
Scribe main entry point.

Modern voice automation platform - Clean break from WhisperWriter.
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging - both file and console
log_dir = Path.home() / ".scribe" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "scribe.log"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler()  # Also log to console
    ]
)

from scribe.__version__ import __version__, BUILD_TIMESTAMP
from scribe.app import ScribeApp
from scribe.core.single_instance import SingleInstanceManager


def main():
    """Main entry point for Scribe."""
    print(f"Scribe v{__version__} - The Open Voice Platform")
    print("Modern voice automation - Phoenix rising!")
    print()

    # Single instance check with version-aware upgrade
    instance_manager = SingleInstanceManager("scribe", __version__, BUILD_TIMESTAMP)
    
    if not instance_manager.acquire():
        print("❌ Another instance of Scribe is already running.")
        print("   Only one instance can run at a time.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    try:
        app = ScribeApp()
        exit_code = app.run()
        instance_manager.release()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nShutting down...")
        instance_manager.release()
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Scribe: {e}")
        import traceback
        traceback.print_exc()
        instance_manager.release()
        sys.exit(1)


if __name__ == "__main__":
    main()
