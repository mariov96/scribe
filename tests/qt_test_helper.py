"""Test utilities for Qt testing."""

import pytest
from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme

class QtTestHelper:
    """Helper class to manage Qt test environment."""
    _app_instance = None
    
    @classmethod
    def get_application(cls):
        """Get or create QApplication instance."""
        if not cls._app_instance:
            print("Creating QApplication in test helper...")
            app = QApplication.instance()
            if not app:
                app = QApplication([])
                app.processEvents()  # Make sure event loop is running
                print("Setting theme...")
                setTheme(Theme.DARK)
                app.processEvents()  # Process theme change events
            cls._app_instance = app
            print(f"Application created/retrieved: {app}")
        return cls._app_instance

# Make the helper available to test modules
@pytest.fixture(scope='session')
def qt_helper():
    """Provide QtTestHelper instance."""
    return QtTestHelper