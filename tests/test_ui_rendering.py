"""
Tests for UI rendering to catch issues like duplicate labels.
"""
import pytest
from PyQt5.QtWidgets import QLabel
from scribe.ui_fluent.pages.home import HomePage

def test_home_page_does_not_have_duplicate_labels(qtbot):
    """
    Test that the HomePage does not contain duplicate labels.
    """
    home_page = HomePage()
    qtbot.addWidget(home_page)

    # Find all QLabel widgets within the HomePage
    labels = home_page.findChildren(QLabel)
    
    # Check for duplicate label text
    label_texts = [label.text() for label in labels if label.text()]
    
    # Assert that there are no duplicate text entries
    assert len(label_texts) == len(set(label_texts)), "Duplicate labels found on the home page"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])