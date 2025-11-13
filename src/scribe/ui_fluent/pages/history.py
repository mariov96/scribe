"""
History Page - View and manage transcription history with two-column layout
"""

import json
import logging
from pathlib import Path
from PyQt5.QtCore import pyqtSignal as Signal, Qt, QDateTime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter,
    QListWidget, QListWidgetItem, QPushButton, QTextEdit, QGridLayout
)
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel, StrongBodyLabel,
    CardWidget, PrimaryPushButton, PushButton, LineEdit,
    ComboBox, FluentIcon as FIF, InfoBar, InfoBarPosition, TextEdit
)
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StarRatingWidget(QWidget):
    """Simple 5-star rating widget"""
    
    valueChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self.star_buttons = []
        for i in range(5):
            btn = QPushButton("☆")
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    font-size: 20px;
                    color: #666;
                }
                QPushButton:hover {
                    color: #FFD700;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i+1: self.setValue(idx))
            self.star_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
    
    def setValue(self, value: int):
        """Set rating value (0-5)"""
        self._value = max(0, min(5, value))
        self._update_stars()
        self.valueChanged.emit()
    
    def value(self) -> int:
        """Get current rating value"""
        return self._value
    
    def _update_stars(self):
        """Update star display"""
        for i, btn in enumerate(self.star_buttons):
            if i < self._value:
                btn.setText("★")
                btn.setStyleSheet("""
                    QPushButton {
                        border: none;
                        background: transparent;
                        font-size: 20px;
                        color: #FFD700;
                    }
                    QPushButton:hover {
                        color: #FFA500;
                    }
                """)
            else:
                btn.setText("☆")
                btn.setStyleSheet("""
                    QPushButton {
                        border: none;
                        background: transparent;
                        font-size: 20px;
                        color: #666;
                    }
                    QPushButton:hover {
                        color: #FFD700;
                    }
                """)


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
        
        # Persistence
        self._history_file = Path.home() / ".scribe" / "data" / "history.json"
        self._history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self._load_history()
        
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
        layout.setSpacing(16)
        
        # Detail title
        self.detail_title = SubtitleLabel("Select a recording")
        self.detail_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # Metrics grid - organized cards
        metrics_container = QWidget()
        metrics_layout = QGridLayout(metrics_container)
        metrics_layout.setSpacing(8)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create metric labels
        self.app_metric = self._create_metric_label("📱 Application", "—")
        self.duration_metric = self._create_metric_label("⏱️ Duration", "—")
        self.confidence_metric = self._create_metric_label("✓ Confidence", "—")
        self.words_metric = self._create_metric_label("📝 Words", "—")
        self.chars_metric = self._create_metric_label("🔤 Characters", "—")
        self.plugin_metric = self._create_metric_label("🔌 Plugin", "—")
        self.ai_metric = self._create_metric_label("🤖 AI Format", "—")
        self.language_metric = self._create_metric_label("🌍 Language", "—")
        
        # Add to grid (2 columns)
        metrics_layout.addWidget(self.app_metric, 0, 0)
        metrics_layout.addWidget(self.duration_metric, 0, 1)
        metrics_layout.addWidget(self.confidence_metric, 1, 0)
        metrics_layout.addWidget(self.words_metric, 1, 1)
        metrics_layout.addWidget(self.chars_metric, 2, 0)
        metrics_layout.addWidget(self.plugin_metric, 2, 1)
        metrics_layout.addWidget(self.ai_metric, 3, 0)
        metrics_layout.addWidget(self.language_metric, 3, 1)
        
        # Quality rating section
        rating_card = CardWidget()
        rating_layout = QVBoxLayout(rating_card)
        rating_layout.setContentsMargins(12, 12, 12, 12)
        rating_layout.setSpacing(8)
        
        rating_header = QHBoxLayout()
        rating_label = StrongBodyLabel("⭐ Quality Rating")
        rating_label.setStyleSheet("font-size: 12px;")
        rating_header.addWidget(rating_label)
        rating_header.addStretch()
        
        self.rating_widget = StarRatingWidget()
        self.rating_widget.valueChanged.connect(self._on_rating_changed)
        
        self.feedback_input = TextEdit()
        self.feedback_input.setPlaceholderText("Optional: Add feedback about transcription quality...")
        self.feedback_input.setFixedHeight(60)
        self.feedback_input.textChanged.connect(self._on_feedback_changed)
        
        rating_layout.addLayout(rating_header)
        rating_layout.addWidget(self.rating_widget)
        rating_layout.addWidget(BodyLabel("Note any errors or issues:"))
        rating_layout.addWidget(self.feedback_input)
        
        # Before/After comparison (if AI formatted)
        self.comparison_widget = QWidget()
        comparison_layout = QVBoxLayout(self.comparison_widget)
        comparison_layout.setContentsMargins(0, 0, 0, 0)
        comparison_layout.setSpacing(8)
        
        comparison_label = StrongBodyLabel("🔄 Before/After AI Formatting")
        comparison_label.setStyleSheet("font-size: 12px;")
        
        self.before_text = QTextEdit()
        self.before_text.setReadOnly(True)
        self.before_text.setFixedHeight(80)
        self.before_text.setPlaceholderText("Original transcription...")
        self.before_text.setStyleSheet("""
            QTextEdit {
                background-color: #2A2A2A;
                border: 1px solid #3F3F3F;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        
        self.after_text = QTextEdit()
        self.after_text.setReadOnly(True)
        self.after_text.setFixedHeight(80)
        self.after_text.setPlaceholderText("AI formatted text...")
        self.after_text.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        
        comparison_layout.addWidget(comparison_label)
        comparison_layout.addWidget(BodyLabel("Before:"))
        comparison_layout.addWidget(self.before_text)
        comparison_layout.addWidget(BodyLabel("After:"))
        comparison_layout.addWidget(self.after_text)
        
        self.comparison_widget.setVisible(False)  # Hidden by default
        
        # Main transcription text area
        text_label = StrongBodyLabel("📄 Transcription")
        text_label.setStyleSheet("font-size: 12px;")
        
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
        layout.addWidget(metrics_container)
        layout.addWidget(rating_card)
        layout.addWidget(self.comparison_widget)
        layout.addWidget(text_label)
        layout.addWidget(self.text_display, 1)
        layout.addLayout(button_layout)
        
        return panel
    
    def _create_metric_label(self, title: str, value: str) -> QWidget:
        """Create a metric display widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        title_label = BodyLabel(title)
        title_label.setStyleSheet("font-size: 10px; color: #888;")
        
        value_label = StrongBodyLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet("font-size: 12px; color: #FFF;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        widget.setStyleSheet("""
            QWidget {
                background-color: #2A2A2A;
                border: 1px solid #3F3F3F;
                border-radius: 4px;
            }
        """)
        
        return widget
    
    # ==================== Event Handlers ====================
    
    def _on_item_selected(self, item: QListWidgetItem):
        """Handle list item selection and show details"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
        
        self._selected_item = entry
        
        # Update detail title
        timestamp = entry.get("timestamp")
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except:
                pass
        
        if hasattr(timestamp, "strftime"):
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = "Unknown time"
        self.detail_title.setText(time_str)
        
        # Update metrics - find value labels inside each metric widget
        self._update_metric_value(self.app_metric, entry.get("application") or "Unknown")
        self._update_metric_value(self.duration_metric, f"{entry.get('audio_duration', 0):.1f}s")
        
        confidence = entry.get("confidence")
        if confidence is not None:
            self._update_metric_value(self.confidence_metric, f"{confidence*100:.0f}%")
        else:
            self._update_metric_value(self.confidence_metric, "—")
        
        self._update_metric_value(self.words_metric, str(entry.get("word_count", 0)))
        self._update_metric_value(self.chars_metric, str(entry.get("character_count", 0)))
        
        # Plugin usage
        used_plugin = entry.get("used_plugin")
        if used_plugin:
            self._update_metric_value(self.plugin_metric, used_plugin)
            self.plugin_metric.setStyleSheet("""
                QWidget {
                    background-color: #2A4A2A;
                    border: 1px solid #4CAF50;
                    border-radius: 4px;
                }
            """)
        else:
            self._update_metric_value(self.plugin_metric, "None")
            self.plugin_metric.setStyleSheet("""
                QWidget {
                    background-color: #2A2A2A;
                    border: 1px solid #3F3F3F;
                    border-radius: 4px;
                }
            """)
        
        # AI formatting
        ai_formatted = entry.get("ai_formatted", False)
        if ai_formatted:
            self._update_metric_value(self.ai_metric, "✓ Applied")
            self.ai_metric.setStyleSheet("""
                QWidget {
                    background-color: #2A3A4A;
                    border: 1px solid #4A9EEA;
                    border-radius: 4px;
                }
            """)
            
            # Show before/after comparison
            raw_text = entry.get("raw_text", "")
            final_text = entry.get("text", "")
            if raw_text and raw_text != final_text:
                self.before_text.setPlainText(raw_text)
                self.after_text.setPlainText(final_text)
                self.comparison_widget.setVisible(True)
            else:
                self.comparison_widget.setVisible(False)
        else:
            self._update_metric_value(self.ai_metric, "—")
            self.ai_metric.setStyleSheet("""
                QWidget {
                    background-color: #2A2A2A;
                    border: 1px solid #3F3F3F;
                    border-radius: 4px;
                }
            """)
            self.comparison_widget.setVisible(False)
        
        # Language
        language = entry.get("language", "Unknown")
        self._update_metric_value(self.language_metric, language.upper() if language else "—")
        
        # Quality rating
        rating = entry.get("quality_rating", 0)
        self.rating_widget.setValue(rating)
        
        # Feedback
        feedback = entry.get("quality_feedback", "")
        self.feedback_input.setPlainText(feedback)
        
        # Update text display
        text = entry.get("text", "")
        self.text_display.setPlainText(text)
        
        # Enable buttons
        self.copy_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
    
    def _update_metric_value(self, metric_widget: QWidget, value: str):
        """Update the value label inside a metric widget"""
        value_label = metric_widget.findChild(StrongBodyLabel, "value")
        if value_label:
            value_label.setText(value)
    
    def _on_rating_changed(self):
        """Handle quality rating change"""
        if not self._selected_item:
            return
        
        rating = self.rating_widget.value()
        self._selected_item["quality_rating"] = rating
        self._save_history()
        
        logger.info(f"Rating updated to {rating} stars for transcription")
    
    def _on_feedback_changed(self):
        """Handle quality feedback change"""
        if not self._selected_item:
            return
        
        feedback = self.feedback_input.toPlainText()
        self._selected_item["quality_feedback"] = feedback
        self._save_history()
        
        logger.debug("Feedback updated for transcription")
    
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
                - used_plugin: str (optional)
                - ai_formatted: bool (optional)
                - raw_text: str (optional)
        """
        # Initialize new fields if not present
        if "quality_rating" not in entry:
            entry["quality_rating"] = 0
        if "quality_feedback" not in entry:
            entry["quality_feedback"] = ""
        
        # Add to internal list
        self._history_items.insert(0, entry)  # Most recent first
        
        # Limit to max items
        if len(self._history_items) > self._max_items:
            self._history_items = self._history_items[:self._max_items]
        
        # Update list widget
        self._refresh_list()
        
        # Save to disk
        self._save_history()
    
    def _save_history(self):
        """Save history to JSON file"""
        try:
            # Convert datetime objects to ISO strings for JSON serialization
            serializable_history = []
            for entry in self._history_items:
                entry_copy = entry.copy()
                if isinstance(entry_copy.get("timestamp"), datetime):
                    entry_copy["timestamp"] = entry_copy["timestamp"].isoformat()
                serializable_history.append(entry_copy)
            
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_history, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"History saved: {len(serializable_history)} items")
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    def _load_history(self):
        """Load history from JSON file"""
        if not self._history_file.exists():
            logger.info("No history file found, starting fresh")
            return
        
        try:
            with open(self._history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert ISO strings back to datetime objects
            for entry in data:
                if isinstance(entry.get("timestamp"), str):
                    try:
                        entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
                    except:
                        entry["timestamp"] = datetime.now()
            
            self._history_items = data[:self._max_items]
            self._refresh_list()
            
            logger.info(f"History loaded: {len(self._history_items)} items")
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self._history_items = []
    
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
