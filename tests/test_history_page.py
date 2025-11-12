"""
Unit tests for History Page UI
"""
import pytest
from datetime import datetime
from PyQt5.QtCore import Qt
from scribe.ui_fluent.pages.history import HistoryPage


class TestHistoryPage:
    """Test suite for History Page"""
    
    def test_history_page_initialization(self, qtbot):
        """Test that history page initializes correctly"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        assert page.isVisible()
        assert len(page._history_items) == 0
    
    def test_add_transcription(self, qtbot, sample_transcription_entry):
        """Test adding a transcription to history"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        page.add_transcription(sample_transcription_entry)
        
        assert len(page._history_items) == 1
        assert page._history_items[0] == sample_transcription_entry
    
    def test_multiple_transcriptions(self, qtbot, sample_transcription_entry):
        """Test adding multiple transcriptions"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        # Add 3 transcriptions
        for i in range(3):
            entry = sample_transcription_entry.copy()
            entry["text"] = f"Transcription {i+1}"
            page.add_transcription(entry)
        
        assert len(page._history_items) == 3
        # Most recent should be first
        assert "Transcription 3" in page._history_items[0]["text"]
    
    def test_max_items_limit(self, qtbot, sample_transcription_entry):
        """Test that history respects max items limit"""
        page = HistoryPage()
        qtbot.addWidget(page)
        page._max_items = 10  # Set small limit for testing
        
        # Add more than max
        for i in range(15):
            entry = sample_transcription_entry.copy()
            entry["text"] = f"Transcription {i+1}"
            page.add_transcription(entry)
        
        # Should be limited to max
        assert len(page._history_items) == 10
        # Most recent should be kept
        assert "Transcription 15" in page._history_items[0]["text"]
    
    def test_stats_update(self, qtbot, sample_transcription_entry):
        """Test that stats card updates correctly"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        page.add_transcription(sample_transcription_entry)
        
        # Check stats labels updated
        assert page.total_label.text() == "1"
        assert page.words_label.text() == "5"
        assert "2" in page.duration_label.text()  # 2.5s rounded
        assert "95%" in page.conf_label.text()
    
    def test_search_functionality(self, qtbot, sample_transcription_entry):
        """Test search filtering"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        # Add entries with different text
        entry1 = sample_transcription_entry.copy()
        entry1["text"] = "Hello world"
        page.add_transcription(entry1)
        
        entry2 = sample_transcription_entry.copy()
        entry2["text"] = "Goodbye world"
        page.add_transcription(entry2)
        
        entry3 = sample_transcription_entry.copy()
        entry3["text"] = "Something else"
        page.add_transcription(entry3)
        
        # Search for "world"
        page.search_input.setText("world")
        page._on_search_changed("world")
        
        # Should show 2 items in list
        assert page.history_list.count() == 2
    
    def test_app_filter(self, qtbot, sample_transcription_entry):
        """Test filtering by application"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        # Add entries from different apps
        entry1 = sample_transcription_entry.copy()
        entry1["application"] = "Chrome"
        page.add_transcription(entry1)
        
        entry2 = sample_transcription_entry.copy()
        entry2["application"] = "VS Code"
        page.add_transcription(entry2)
        
        entry3 = sample_transcription_entry.copy()
        entry3["application"] = "Chrome"
        page.add_transcription(entry3)
        
        # Filter by Chrome
        page.app_filter.setCurrentText("Chrome")
        page._on_filter_changed("Chrome")
        
        # Should show 2 Chrome entries
        assert page.history_list.count() == 2
    
    def test_clear_filters(self, qtbot, sample_transcription_entry):
        """Test clearing filters shows all items"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        # Add 3 entries
        for i in range(3):
            entry = sample_transcription_entry.copy()
            page.add_transcription(entry)
        
        # Apply search filter
        page.search_input.setText("test")
        page._on_search_changed("test")
        
        # Clear filters
        page._clear_filters()
        
        # Should show all 3 entries
        assert page.history_list.count() == 3
        assert page.search_input.text() == ""
    
    def test_item_selection(self, qtbot, sample_transcription_entry):
        """Test selecting an item updates detail view"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        page.add_transcription(sample_transcription_entry)
        
        # Simulate clicking first item
        item = page.history_list.item(0)
        page._on_item_selected(item)
        
        # Check detail view updated
        assert sample_transcription_entry["text"] in page.detail_text.text()
    
    def test_clear_history(self, qtbot, sample_transcription_entry):
        """Test clearing all history"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        # Add some entries
        for i in range(3):
            page.add_transcription(sample_transcription_entry)
        
        assert len(page._history_items) == 3
        
        # Clear history
        page.clear_history()
        
        assert len(page._history_items) == 0
        assert page.history_list.count() == 0
        assert page.total_label.text() == "0"
    
    def test_get_history(self, qtbot, sample_transcription_entry):
        """Test retrieving history data"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        page.add_transcription(sample_transcription_entry)
        
        history = page.get_history()
        
        assert len(history) == 1
        assert history[0] == sample_transcription_entry
        # Should be a copy, not reference
        assert history is not page._history_items
    
    def test_load_history(self, qtbot, sample_transcription_entry):
        """Test loading saved history"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        # Prepare history data
        history_data = [sample_transcription_entry for _ in range(3)]
        
        # Load it
        page.load_history(history_data)
        
        assert len(page._history_items) == 3
        assert page.history_list.count() == 3
    
    def test_format_list_item(self, qtbot, sample_transcription_entry):
        """Test list item formatting"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        formatted = page._format_list_item(sample_transcription_entry)
        
        # Check key elements are in formatted string
        assert "Test App" in formatted
        assert "2.5s" in formatted
        assert "5 words" in formatted
        assert "95%" in formatted
        assert sample_transcription_entry["text"] in formatted
    
    def test_app_filter_updates(self, qtbot, sample_transcription_entry):
        """Test that app filter dropdown updates with new apps"""
        page = HistoryPage()
        qtbot.addWidget(page)
        
        # Initially should only have "All Applications"
        initial_count = page.app_filter.count()
        
        # Add entry with new app
        entry = sample_transcription_entry.copy()
        entry["application"] = "New App"
        page.add_transcription(entry)
        
        # Filter should now include the new app
        assert page.app_filter.count() > initial_count
        
        # Check "New App" is in filter
        found = False
        for i in range(page.app_filter.count()):
            if page.app_filter.itemText(i) == "New App":
                found = True
                break
        assert found is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
