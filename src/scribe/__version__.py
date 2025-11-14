"""Version information for Scribe."""
import time

VERSION = (2, 0, 1)

__version__ = "2.0.1"

# Build timestamp - updated automatically on each build/commit
# Format: Unix timestamp (seconds since epoch)
BUILD_TIMESTAMP = 1763067100  # 2025-11-13 12:51:40


def get_version():
    """Return the version string."""
    return __version__


def get_version_tuple():
    """Return the version as a tuple."""
    return VERSION


def get_build_timestamp():
    """Return the build timestamp."""
    return BUILD_TIMESTAMP


def get_version_info():
    """Return full version info including build timestamp."""
    return {
        "version": __version__,
        "version_tuple": VERSION,
        "build_timestamp": BUILD_TIMESTAMP
    }
