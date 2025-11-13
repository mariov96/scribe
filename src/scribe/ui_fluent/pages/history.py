"""
History Page - View and manage transcription history with two-column layout
"""

from PyQt5.QtCore import pyqtSignal as Signal, Qt, QDateTime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter,
    QListWidget, QListWidgetItem, QPushButton, QTextEdit
)
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel, StrongBodyLabel,
    CardWidget, PrimaryPushButton, PushButton, LineEdit,
    ComboBox, FluentIcon as FIF, InfoBar, InfoBarPosition
)
from typing import Dict, Any, List, Optional
from datetime import datetime


class HistoryPage(QWidget):
    """
    History page with two-column layout: 25% list, 75% details.
    
    Features:
    - Compact list of transcriptions on the left (25%)
    - Full details panel on the right (75%)
    - Click to view full text and metadata
    - Search and filter capabilities
    """
    
    # Signals
    transcription_selected = Signal(dict)  # Emits selected transcription data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HistoryPage")
        
        # History data
        self._history_items: List[Dict[str, Any]] = []
        self._max_items = 100
        self._selected_item = None
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)
        
        # Header
        header_layout = QVBoxLayout()
        title = TitleLabel("Transcription History")
        subtitle = BodyLabel("Click a recording to view details")
        subtitle.setStyleSheet("color: #808080; font-size: 12px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addSpacing(4)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("🔍 Search transcriptions...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)
        
        # Splitter for 25/75 layout
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: List (25%)
        self.list_panel = self._create_list_panel()
        
        # Right panel: Details (75%)
        self.detail_panel = self._create_detail_panel()
        
        self.splitter.addWidget(self.list_panel)
        self.splitter.addWidget(self.detail_panel)
        self.splitter.setStretchFactor(0, 1)  # List gets 1 part
        self.splitter.setStretchFactor(1, 3)  # Details gets 3 parts (75%)
        
        main_layout.addLayout(header_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.splitter, 1)
    
    def _create_list_panel(self):
        """Create left panel with transcription list"""
        panel = CardWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # List title
        list_title = BodyLabel("Recordings")
        list_title.setStyleSheet("font-weight: bold; font-size: 11px;")
        
        # List widget
        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.history_list.itemClicked.connect(self._on_item_selected)
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #2D2D2D;
                border: 1px solid #3F3F3F;
                border-radius: 4px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3F3F3F;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3A3A3A;
            }
        """)
        
        # Count label
        self.count_label = BodyLabel("0 recordings")
        self.count_label.setStyleSheet("color: #808080; font-size: 10px;")
        
        layout.addWidget(list_title)
        layout.addWidget(self.history_list, 1)
        layout.addWidget(self.count_label)
        
        return panel
    
    def _create_detail_panel(self):
        """Create right panel with selected recording details"""
        panel = CardWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Detail title
        self.detail_title = SubtitleLabel("Select a recording")
        self.detail_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # Metadata row
        self.metadata_widget = QWidget()
        meta_layout = QHBoxLayout(self.metadata_widget)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(16)
        
        self.timestamp_label = BodyLabel("—")
        self.app_label = BodyLabel("—")
        self.duration_label = BodyLabel("—")
        self.confidence_label = BodyLabel("—")
        
        meta_layout.addWidget(QLabel("🕐"))
        meta_layout.addWidget(self.timestamp_label)
        meta_layout.addWidget(QLabel("📱"))
        meta_layout.addWidget(self.app_label)
        meta_layout.addWidget(QLabel("⏱️"))
        meta_layout.addWidget(self.duration_label)
        meta_layout.addWidget(QLabel("✓"))
        meta_layout.addWidget(self.confidence_label)
        meta_layout.addStretch()
        
        self.metadata_widget.setStyleSheet("font-size: 11px; color: #B0B0B0;")
        
        # Transcription text area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText("Select a recording to view transcription...")
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                border: 1px solid #3F3F3F;
                border-radius: 4px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.copy_btn = PrimaryPushButton(FIF.COPY, "Copy Text")
        self.copy_btn.clicked.connect(self._copy_text)
        self.copy_btn.setEnabled(False)
        
        self.delete_btn = PushButton(FIF.DELETE, "Delete")
        self.delete_btn.clicked.connect(self._delete_item)
        self.delete_btn.setEnabled(False)
        
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addWidget(self.detail_title)
        layout.addWidget(self.metadata_widget)
        layout.addWidget(self.text_display, 1)
        layout.addLayout(button_layout)
        
        return panel
    
    # ==================== Event Handlers ====================
    
    def _on_item_selected(self, item: QListWidgetItem):
        """Handle list item selection and show details"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
        
        self._selected_item = entry
        
        # Update detail title
        timestamp = entry.get("timestamp")
        if hasattr(timestamp, "strftime"):
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = "Unknown time"
        self.detail_title.setText(time_str)
        
        # Update metadata
        self.timestamp_label.setText(time_str)
        self.app_label.setText(entry.get("application") or "Unknown")
        self.duration_label.setText(f"{entry.get('audio_duration', 0):.1f}s")
        
        confidence = entry.get("confidence")
        if confidence is not None:
            self.confidence_label.setText(f"{confidence*100:.0f}%")
        else:
            self.confidence_label.setText("—")
        
        # Update text display
        text = entry.get("text", "")
        self.text_display.setPlainText(text)
        
        # Enable buttons
        self.copy_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
    
    def _on_search_changed(self, text: str):
        """Filter list by search text"""
        search = text.lower().strip()
        
        if not search:
            self._refresh_list()
            return
        
        # Filter items
        filtered = [
            entry for entry in self._history_items
            if search in entry.get("text", "").lower()
            or search in entry.get("application", "").lower()
        ]
        
        self._refresh_list(filtered)
    
    def _copy_text(self):
        """Copy selected transcription text to clipboard"""
        if not self._selected_item:
            return
        
        text = self._selected_item.get("text", "")
        if text:
            from PyQt5.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            InfoBar.success(
                title="Copied!",
                content="Transcription copied to clipboard",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP
            )
    
    def _delete_item(self):
        """Delete selected transcription"""
        if not self._selected_item:
            return
        
        # Remove from list
        if self._selected_item in self._history_items:
            self._history_items.remove(self._selected_item)
        
        # Clear selection
        self._selected_item = None
        self.detail_title.setText("Select a recording")
        self.text_display.clear()
        self.copy_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        
        # Refresh
        self._refresh_list()
        
        InfoBar.success(
            title="Deleted",
            content="Transcription removed from history",
            parent=self,
            duration=2000,
            position=InfoBarPosition.TOP
        )
    
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
    
    def _refresh_list(self, filtered_items: Optional[List[Dict[str, Any]]] = None):
        """Refresh the list widget with current or filtered items"""
        self.history_list.clear()
        
        items_to_show = filtered_items if filtered_items is not None else self._history_items
        
        for entry in items_to_show:
            item_text = self._format_list_item(entry)
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.history_list.addItem(item)
        
        # Update count
        self.count_label.setText(f"{len(items_to_show)} recordings")
    
    def _format_list_item(self, entry: Dict[str, Any]) -> str:
        """Format a transcription entry for compact list display"""
        timestamp = entry.get("timestamp")
        if hasattr(timestamp, "strftime"):
            time_str = timestamp.strftime("%H:%M")
        else:
            time_str = "??"
        
        # Preview of text (first 30 chars)
        text = entry.get("text", "")
        preview = text[:30] + "..." if len(text) > 30 else text
        preview = preview.replace("\n", " ")
        
        words = entry.get("word_count", 0)
        
        return f"{time_str} • {words}w\n{preview}"
