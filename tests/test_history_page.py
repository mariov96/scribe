"""
Unit tests for History Page UI with Database Integration
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock

# PyQt is now mocked in conftest.py

from scribe.ui_fluent.pages.history import HistoryPage
from scribe.core.database import DatabaseManager

@pytest.fixture
def db_manager():
    """Fixture to create an in-memory SQLite database for testing."""
    db = DatabaseManager(db_path=":memory:")
    db.connect()
    db.create_schema()
    yield db
    db.close()

@pytest.fixture
def history_page(qtbot, db_manager, monkeypatch):
    """Fixture to create a HistoryPage instance with a mocked DB manager."""
    # Mock the DatabaseManager constructor to return our in-memory DB
    monkeypatch.setattr(HistoryPage, "__init__", lambda self, parent=None: None)
    page = HistoryPage(parent=None)
    
    # Manually initialize what the original __init__ would have done
    page.db = db_manager
    page.setObjectName("HistoryPage")
    page._history_items = []
    page._max_items = 100
    page._selected_item = None
    
    # Mock the UI creation methods as we are not testing the full UI rendering
    page._create_list_panel = MagicMock()
    page._create_detail_panel = MagicMock()
    page.load_history = MagicMock() # Mock load_history to prevent it from running in this setup

    qtbot.addWidget(page)
    return page

@pytest.fixture
def sample_transcription_entry():
    """Provides a sample transcription entry dictionary."""
    return {
        "timestamp": datetime.now(),
        "text": "This is a test transcription.",
        "application": "Test App",
        "window_title": "Test Window",
        "audio_duration": 2.5,
        "word_count": 5,
        "character_count": 29,
        "confidence": 0.95,
        "language": "en",
        "used_plugin": None,
        "ai_formatted": False,
        "raw_text": "this is a test transcription",
        "quality_rating": 0,
        "quality_feedback": "",
        "audio_file": "/path/to/test.wav"
    }

class TestHistoryPageWithDB:
    """Test suite for History Page with database integration."""

    def test_history_page_initialization(self, history_page):
        """Test that history page initializes correctly with a database connection."""
        assert history_page.db is not None
        assert history_page.db.conn is not None

    def test_add_transcription_to_db(self, history_page, sample_transcription_entry):
        """Test adding a transcription to the database."""
        history_page.add_transcription(sample_transcription_entry)
        
        # Verify that load_history was called, which would refresh the UI
        history_page.load_history.assert_called_once()

        # Verify directly in the database
        cursor = history_page.db.conn.cursor()
        cursor.execute("SELECT * FROM transcriptions")
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0]["text"] == sample_transcription_entry["text"]

    def test_load_history_from_db(self, history_page, sample_transcription_entry, monkeypatch):
        """Test loading history from the database."""
        # Un-mock the load_history method for this test
        monkeypatch.setattr(history_page, "load_history", HistoryPage.load_history.__get__(history_page, HistoryPage))
        monkeypatch.setattr(history_page, "_refresh_list", MagicMock())

        # Add an entry directly to the DB to simulate existing data
        history_page.add_transcription(sample_transcription_entry)

        # Call load_history
        history_page.load_history()

        # Check that the internal list is populated
        assert len(history_page._history_items) == 1
        assert history_page._history_items[0]["text"] == sample_transcription_entry["text"]
        history_page._refresh_list.assert_called_once()

    def test_clear_history_from_db(self, history_page, sample_transcription_entry, monkeypatch):
        """Test clearing all history from the database."""
        # Un-mock the clear_history method for this test
        monkeypatch.setattr(history_page, "clear_history", HistoryPage.clear_history.__get__(history_page, HistoryPage))
        monkeypatch.setattr(history_page, "load_history", MagicMock())

        # Add some entries
        history_page.add_transcription(sample_transcription_entry)
        history_page.add_transcription(sample_transcription_entry)
        
        # Clear history
        history_page.clear_history()
        
        # Verify in the database
        cursor = history_page.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transcriptions")
        count = cursor.fetchone()[0]
        assert count == 0
        history_page.load_history.assert_called_once()

    def test_delete_item_from_db(self, history_page, sample_transcription_entry, monkeypatch):
        """Test deleting a single item from the database."""
        # Un-mock the delete_item method for this test
        monkeypatch.setattr(history_page, "_delete_item", HistoryPage._delete_item.__get__(history_page, HistoryPage))
        monkeypatch.setattr(history_page, "load_history", MagicMock())

        # Add an entry and set it as selected
        history_page.add_transcription(sample_transcription_entry)
        cursor = history_page.db.conn.cursor()
        cursor.execute("SELECT * FROM transcriptions LIMIT 1")
        item_to_delete = dict(cursor.fetchone())
        history_page._selected_item = item_to_delete

        # Delete the item
        history_page._delete_item()

        # Verify in the database
        cursor.execute("SELECT COUNT(*) FROM transcriptions")
        count = cursor.fetchone()[0]
        assert count == 0
        history_page.load_history.assert_called_once()

    def test_search_history_in_db(self, history_page, sample_transcription_entry, monkeypatch):
        """Test searching history in the database."""
        # Un-mock the search method for this test
        monkeypatch.setattr(history_page, "_on_search_changed", HistoryPage._on_search_changed.__get__(history_page, HistoryPage))
        monkeypatch.setattr(history_page, "_refresh_list", MagicMock())
        monkeypatch.setattr(history_page, "load_history", MagicMock())

        # Add entries with different text
        entry1 = sample_transcription_entry.copy()
        entry1["text"] = "Hello world from Scribe"
        history_page.add_transcription(entry1)
        
        entry2 = sample_transcription_entry.copy()
        entry2["text"] = "Goodbye from the test suite"
        history_page.add_transcription(entry2)

        # Search for "Scribe"
        history_page._on_search_changed("Scribe")

        # Check that the internal list is filtered
        assert len(history_page._history_items) == 1
        assert history_page._history_items[0]["text"] == "Hello world from Scribe"
        history_page._refresh_list.assert_called_once()
