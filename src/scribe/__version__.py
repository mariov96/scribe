"""Version information for Scribe."""

VERSION = (2, 0, 0, "alpha")

__version__ = "2.0.0-alpha"


def get_version():
    """Return the version string."""
    return __version__


def get_version_tuple():
    """Return the version as a tuple."""
    return VERSION
