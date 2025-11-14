#!/usr/bin/env python3
"""
Update build timestamp in __version__.py

This script should be run:
- Before creating a release
- After making significant changes
- As part of CI/CD pipeline

Usage:
    python tools/update_build_timestamp.py
"""

import sys
import time
from pathlib import Path
from datetime import datetime


def update_build_timestamp():
    """Update BUILD_TIMESTAMP in __version__.py to current time."""
    
    # Get path to __version__.py
    repo_root = Path(__file__).parent.parent
    version_file = repo_root / "src" / "scribe" / "__version__.py"
    
    if not version_file.exists():
        print(f"❌ Error: {version_file} not found")
        sys.exit(1)
    
    # Read current content
    content = version_file.read_text(encoding='utf-8')
    
    # Generate new timestamp
    new_timestamp = int(time.time())
    timestamp_str = datetime.fromtimestamp(new_timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    # Find and replace BUILD_TIMESTAMP line
    lines = content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('BUILD_TIMESTAMP ='):
            # Keep any comment on the line
            comment = ""
            if '#' in line:
                comment = " " + line.split('#', 1)[1]
            
            lines[i] = f"BUILD_TIMESTAMP = {new_timestamp}  # {timestamp_str}"
            updated = True
            break
    
    if not updated:
        print("❌ Error: BUILD_TIMESTAMP not found in __version__.py")
        sys.exit(1)
    
    # Write updated content
    new_content = '\n'.join(lines)
    version_file.write_text(new_content, encoding='utf-8')
    
    # Show current version info
    version = None
    for line in lines:
        if line.strip().startswith('__version__ ='):
            version = line.split('=')[1].strip().strip('"\'')
            break
    
    print(f"✅ Build timestamp updated!")
    print(f"   Version: {version}")
    print(f"   Build time: {timestamp_str}")
    print(f"   Timestamp: {new_timestamp}")
    print(f"\n   File: {version_file}")


if __name__ == "__main__":
    update_build_timestamp()
