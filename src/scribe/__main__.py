"""
Scribe main entry point.

Modern voice automation platform - Clean break from WhisperWriter.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Setup logging - both file and console with timestamp
log_dir = Path.home() / ".scribe" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# Create timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"scribe_{timestamp}.log"

# Clean up old log files (keep only last 10)
try:
    log_files = sorted(log_dir.glob("scribe_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old_log in log_files[10:]:  # Keep 10 most recent
        try:
            old_log.unlink()
        except Exception:
            pass  # Ignore errors deleting old logs
except Exception:
    pass  # Ignore errors during cleanup

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),  # mode='w' for new file each run
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
