"""
History Page - View and manage transcription history
"""

from PyQt5.QtCore import pyqtSignal as Signal, Qt, QDateTime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QPushButton
)
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel,
    CardWidget, PrimaryPushButton, PushButton, LineEdit,
    ComboBox, FluentIcon as FIF, InfoBar, InfoBarPosition
)
from typing import Dict, Any, List, Optional
from datetime import datetime


class HistoryPage(ScrollArea):
    """
    History page showing transcription history with metadata.
    
    Features:
    - List of last 50-100 transcriptions
    - Click to view full text
    - Metadata: timestamp, app, duration, confidence
    - Search and filter capabilities (future)
    """
    
    # Signals
    transcription_selected = Signal(dict)  # Emits selected transcription data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HistoryPage")
        
        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        
        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)
        self.vBoxLayout.setSpacing(20)
        
        # History data
        self._history_items: List[Dict[str, Any]] = []
        self._max_items = 100
        
        # UI Components
        self._create_header()
        self._create_stats_card()
        self._create_search_filter()
        self._create_history_list()
        self._create_detail_view()
        
        self.vBoxLayout.addStretch(1)
    
    def _create_header(self):
        """Create page header"""
        title = TitleLabel("Transcription History")
        subtitle = BodyLabel("View and search your past transcriptions")
        subtitle.setStyleSheet("color: #808080; font-size: 12px;")
        
        self.vBoxLayout.addWidget(title)
        self.vBoxLayout.addWidget(subtitle)
        self.vBoxLayout.addSpacing(8)
    
    def _create_stats_card(self):
        """Create quick stats card"""
        card = CardWidget()
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(32)
        
        # Total count
        total_container = QVBoxLayout()
        self.total_label = SubtitleLabel("0")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_subtitle = BodyLabel("Total")
        total_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_subtitle.setStyleSheet("color: #808080; font-size: 11px;")
        total_container.addWidget(self.total_label)
        total_container.addWidget(total_subtitle)
        
        # Total words
        words_container = QVBoxLayout()
        self.words_label = SubtitleLabel("0")
        self.words_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        words_subtitle = BodyLabel("Total Words")
        words_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        words_subtitle.setStyleSheet("color: #808080; font-size: 11px;")
        words_container.addWidget(self.words_label)
        words_container.addWidget(words_subtitle)
        
        # Total duration
        duration_container = QVBoxLayout()
        self.duration_label = SubtitleLabel("0s")
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duration_subtitle = BodyLabel("Total Duration")
        duration_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duration_subtitle.setStyleSheet("color: #808080; font-size: 11px;")
        duration_container.addWidget(self.duration_label)
        duration_container.addWidget(duration_subtitle)
        
        # Avg confidence
        conf_container = QVBoxLayout()
        self.conf_label = SubtitleLabel("—")
        self.conf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        conf_subtitle = BodyLabel("Avg Confidence")
        conf_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        conf_subtitle.setStyleSheet("color: #808080; font-size: 11px;")
        conf_container.addWidget(self.conf_label)
        conf_container.addWidget(conf_subtitle)
        
        layout.addLayout(total_container)
        layout.addLayout(words_container)
        layout.addLayout(duration_container)
        layout.addLayout(conf_container)
        layout.addStretch()
        
        self.vBoxLayout.addWidget(card)
    
    def _create_search_filter(self):
        """Create search and filter controls"""
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Search box
        search_row = QHBoxLayout()
        search_label = BodyLabel("Search:")
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Search transcriptions...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self._on_search_changed)
        
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_input)
        search_row.addStretch()
        
        # Filter row
        filter_row = QHBoxLayout()
        filter_label = BodyLabel("Filter by App:")
        self.app_filter = ComboBox()
        self.app_filter.addItem("All Applications")
        self.app_filter.setFixedWidth(200)
        self.app_filter.currentTextChanged.connect(self._on_filter_changed)
        
        clear_btn = PushButton(FIF.DELETE, "Clear Filters")
        clear_btn.clicked.connect(self._clear_filters)
        
        filter_row.addWidget(filter_label)
        filter_row.addWidget(self.app_filter)
        filter_row.addSpacing(16)
        filter_row.addWidget(clear_btn)
        filter_row.addStretch()
        
        layout.addLayout(search_row)
        layout.addLayout(filter_row)
        
        self.vBoxLayout.addWidget(card)
    
    def _create_history_list(self):
        """Create history list widget"""
        list_card = CardWidget()
        layout = QVBoxLayout(list_card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        list_header = SubtitleLabel("Recent Transcriptions")
        layout.addWidget(list_header)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3F3F3F;
                min-height: 60px;
            }
            QListWidget::item:selected {
                background-color: rgba(0, 120, 212, 0.3);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
        self.history_list.itemClicked.connect(self._on_item_selected)
        
        layout.addWidget(self.history_list)
        
        self.vBoxLayout.addWidget(list_card, 2)  # Give it 2x space
    
    def _create_detail_view(self):
        """Create detail view for selected transcription"""
        detail_card = CardWidget()
        layout = QVBoxLayout(detail_card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        header_row = QHBoxLayout()
        detail_header = SubtitleLabel("Selected Transcription")
        
        copy_btn = PushButton(FIF.COPY, "Copy Text")
        copy_btn.clicked.connect(self._copy_selected_text)
        
        header_row.addWidget(detail_header)
        header_row.addStretch()
        header_row.addWidget(copy_btn)
        
        layout.addLayout(header_row)
        
        # Detail text
        self.detail_text = BodyLabel("Select a transcription to view details")
        self.detail_text.setWordWrap(True)
        self.detail_text.setStyleSheet("""
            QLabel {
                background-color: rgba(80, 80, 80, 0.2);
                border-radius: 8px;
                padding: 16px;
                font-size: 12px;
                line-height: 1.6;
            }
        """)
        self.detail_text.setMinimumHeight(120)
        
        layout.addWidget(self.detail_text)
        
        self.vBoxLayout.addWidget(detail_card, 1)
    
    # ==================== Data Management ====================
    
    def add_transcription(self, entry: Dict[str, Any]):
        """
        Add a new transcription to history.
        
        Args:
            entry: Transcription data with keys:
                - timestamp: datetime
                - text: str
                - application: str
                - window_title: str
                - audio_duration: float
                - word_count: int
                - character_count: int
                - confidence: float (optional)
        """
        # Add to internal list
        self._history_items.insert(0, entry)  # Most recent first
        
        # Limit to max items
        if len(self._history_items) > self._max_items:
            self._history_items = self._history_items[:self._max_items]
        
        # Update list widget
        self._refresh_list()
        
        # Update stats
        self._update_stats()
        
        # Update app filter dropdown
        self._update_app_filter()
    
    def _refresh_list(self, filtered_items: Optional[List[Dict[str, Any]]] = None):
        """Refresh the list widget with current or filtered items"""
        self.history_list.clear()
        
        items_to_show = filtered_items if filtered_items is not None else self._history_items
        
        for entry in items_to_show:
            item_text = self._format_list_item(entry)
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.history_list.addItem(item)
    
    def _format_list_item(self, entry: Dict[str, Any]) -> str:
        """Format a transcription entry for list display"""
        timestamp = entry.get("timestamp")
        if hasattr(timestamp, "strftime"):
            time_str = timestamp.strftime("%H:%M:%S")
            date_str = timestamp.strftime("%Y-%m-%d")
        else:
            time_str = "??:??:??"
            date_str = "????-??-??"
        
        app = entry.get("application") or "Unknown"
        duration = entry.get("audio_duration", 0)
        words = entry.get("word_count", 0)
        chars = entry.get("character_count", 0)
        confidence = entry.get("confidence")
        
        conf_str = f"{confidence*100:.0f}%" if confidence is not None else "—"
        
        # Preview of text (first 80 chars)
        text = entry.get("text", "")
        preview = text[:80] + "..." if len(text) > 80 else text
        preview = preview.replace("\n", " ")
        
        return (
            f"📅 {date_str} {time_str} • 💻 {app}\n"
            f"⏱️ {duration:.1f}s • 📝 {words} words / {chars} chars • ✨ {conf_str}\n"
            f"{preview}"
        )
    
    def _update_stats(self):
        """Update the statistics card"""
        if not self._history_items:
            self.total_label.setText("0")
            self.words_label.setText("0")
            self.duration_label.setText("0s")
            self.conf_label.setText("—")
            return
        
        total = len(self._history_items)
        total_words = sum(e.get("word_count", 0) for e in self._history_items)
        total_duration = sum(e.get("audio_duration", 0) for e in self._history_items)
        
        confidences = [e.get("confidence") for e in self._history_items if e.get("confidence") is not None]
        avg_conf = sum(confidences) / len(confidences) if confidences else None
        
        self.total_label.setText(str(total))
        self.words_label.setText(f"{total_words:,}")
        self.duration_label.setText(f"{total_duration:.0f}s")
        
        if avg_conf is not None:
            self.conf_label.setText(f"{avg_conf*100:.0f}%")
        else:
            self.conf_label.setText("—")
    
    def _update_app_filter(self):
        """Update the application filter dropdown with unique apps"""
        current_apps = set(e.get("application", "Unknown") for e in self._history_items)
        
        # Save current selection
        current_selection = self.app_filter.currentText()
        
        # Clear and rebuild
        self.app_filter.clear()
        self.app_filter.addItem("All Applications")
        
        for app in sorted(current_apps):
            if app and app != "Unknown":
                self.app_filter.addItem(app)
        
        # Restore selection if it still exists
        if current_selection != "All Applications":
            index = self.app_filter.findText(current_selection)
            if index >= 0:
                self.app_filter.setCurrentIndex(index)
    
    # ==================== Event Handlers ====================
    
    def _on_item_selected(self, item: QListWidgetItem):
        """Handle list item selection"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
        
        # Update detail view
        text = entry.get("text", "No text available")
        
        timestamp = entry.get("timestamp")
        if hasattr(timestamp, "strftime"):
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = "Unknown time"
        
        app = entry.get("application") or "Unknown"
        duration = entry.get("audio_duration", 0)
        words = entry.get("word_count", 0)
        chars = entry.get("character_count", 0)
        confidence = entry.get("confidence")
        conf_str = f"{confidence*100:.0f}%" if confidence is not None else "—"
        
        detail_html = f"""
        <p><b>📅 Time:</b> {time_str}</p>
        <p><b>💻 Application:</b> {app}</p>
        <p><b>⏱️ Duration:</b> {duration:.1f}s &nbsp; | &nbsp; <b>📝 Words:</b> {words} &nbsp; | &nbsp; <b>🔤 Chars:</b> {chars} &nbsp; | &nbsp; <b>✨ Confidence:</b> {conf_str}</p>
        <hr style="border: 1px solid #3F3F3F;">
        <p><b>Transcription:</b></p>
        <p>{text}</p>
        """
        
        self.detail_text.setText(detail_html)
        self.detail_text.setTextFormat(Qt.TextFormat.RichText)
        
        # Store selected entry for copy operation
        self._selected_entry = entry
        
        # Emit signal
        self.transcription_selected.emit(entry)
    
    def _on_search_changed(self, text: str):
        """Handle search text change"""
        search_term = text.lower().strip()
        
        if not search_term:
            self._refresh_list()
            return
        
        # Filter items by search term
        filtered = [
            entry for entry in self._history_items
            if search_term in entry.get("text", "").lower()
            or search_term in entry.get("application", "").lower()
        ]
        
        self._refresh_list(filtered)
    
    def _on_filter_changed(self, app_name: str):
        """Handle application filter change"""
        if app_name == "All Applications":
            self._refresh_list()
            return
        
        # Filter by application
        filtered = [
            entry for entry in self._history_items
            if entry.get("application") == app_name
        ]
        
        self._refresh_list(filtered)
    
    def _clear_filters(self):
        """Clear all filters and search"""
        self.search_input.clear()
        self.app_filter.setCurrentIndex(0)
        self._refresh_list()
    
    def _copy_selected_text(self):
        """Copy selected transcription to clipboard"""
        if not hasattr(self, "_selected_entry") or not self._selected_entry:
            InfoBar.warning(
                title="No Selection",
                content="Please select a transcription first",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            return
        
        text = self._selected_entry.get("text", "")
        
        if text:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            InfoBar.success(
                title="Copied!",
                content="Transcription text copied to clipboard",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=1500,
                parent=self
            )
    
    # ==================== Public API ====================
    
    def clear_history(self):
        """Clear all history"""
        self._history_items.clear()
        self._refresh_list()
        self._update_stats()
        self._update_app_filter()
        self.detail_text.setText("Select a transcription to view details")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get all history items"""
        return self._history_items.copy()
    
    def load_history(self, items: List[Dict[str, Any]]):
        """Load history from saved data"""
        self._history_items = items[:self._max_items]
        self._refresh_list()
        self._update_stats()
        self._update_app_filter()
