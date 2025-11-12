"""
Transcription Page - Main recording interface
"""

from PyQt5.QtCore import pyqtSignal as Signal, QTimer, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QProgressBar
from typing import Any, Dict, Optional
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel,
    CardWidget, PrimaryPushButton, ComboBox, TextEdit,
    FluentIcon as FIF
)


class TranscriptionPage(ScrollArea):
    """Main transcription interface"""
    
    start_recording = Signal()
    stop_recording = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TranscriptionPage")
        
        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        
        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)
        self.vBoxLayout.setSpacing(20)
        
        title = TitleLabel("Transcription")
        control_card = self._create_controls()
        
        output_label = SubtitleLabel("Output")
        self.output_text = TextEdit()
        self.output_text.setPlaceholderText("Transcribed text will appear here...")
        self.output_text.setMinimumHeight(150)
        self.output_text.setStyleSheet("font-size: 12px;")

        insights_label = SubtitleLabel("Session Insights")
        self.summary_card = self._create_summary_card()

        history_label = SubtitleLabel("Transcription History")
        self.history_card = self._create_history_card()
        
        self.vBoxLayout.addWidget(title)
        self.vBoxLayout.addWidget(control_card)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(output_label)
        self.vBoxLayout.addWidget(self.output_text, 1)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(insights_label)
        self.vBoxLayout.addWidget(self.summary_card)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(history_label)
        self.vBoxLayout.addWidget(self.history_card, 1)
    
    def _create_controls(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        status_row = QHBoxLayout()
        self.status_icon = QLabel("⚫")
        self.status_icon.setStyleSheet("font-size: 16px;")
        self.status_label = SubtitleLabel("Ready")
        status_row.addWidget(self.status_icon)
        status_row.addWidget(self.status_label)
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        self.level_bar.setTextVisible(False)
        self.level_bar.setFixedWidth(140)
        self.level_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #1f1f1f;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        status_row.addWidget(self.level_bar)
        status_row.addStretch()
        
        self.record_btn = PrimaryPushButton(FIF.MICROPHONE, "Start Recording")
        self.record_btn.setFixedSize(200, 48)
        self.record_btn.clicked.connect(self._toggle_recording)
        
        settings_row = QHBoxLayout()
        lang_label = BodyLabel("Language:")
        lang_combo = ComboBox()
        lang_combo.addItems(["English", "Spanish", "French", "German", "Chinese"])
        lang_combo.setFixedWidth(150)
        
        model_label = BodyLabel("Model:")
        model_combo = ComboBox()
        model_combo.addItems(["base", "small", "medium", "large-v3"])
        model_combo.setCurrentIndex(2)
        model_combo.setFixedWidth(150)
        
        settings_row.addWidget(lang_label)
        settings_row.addWidget(lang_combo)
        settings_row.addSpacing(24)
        settings_row.addWidget(model_label)
        settings_row.addWidget(model_combo)
        settings_row.addStretch()
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.record_btn)
        btn_row.addStretch()
        
        layout.addLayout(status_row)
        layout.addLayout(btn_row)
        layout.addLayout(settings_row)
        
        self.recording = False
        return card
    
    def _create_summary_card(self):
        card = CardWidget()
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(20)

        def make_metric(title: str, subtitle: str):
            container = QVBoxLayout()
            label = TitleLabel("—")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub = BodyLabel(subtitle)
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container.addWidget(BodyLabel(title))
            container.addWidget(label)
            container.addWidget(sub)
            return container, label

        self.summary_labels: Dict[str, QLabel] = {}
        metrics = [
            ("total", "Sessions Today"),
            ("avg_words", "Avg words / event"),
            ("avg_duration", "Avg duration"),
            ("avg_confidence", "Avg confidence"),
        ]
        for key, subtitle in metrics:
            container, label = make_metric(key.replace("_", " ").title(), subtitle)
            layout.addLayout(container)
            self.summary_labels[key] = label

        layout.addStretch()
        return card

    def _create_history_card(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(10)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("font-size: 11px;")
        self.history_list.itemClicked.connect(self._on_history_selected)

        layout.addWidget(self.history_list)
        return card
    
    def _toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.status_icon.setText("🔴")
            self.status_label.setText("Recording...")
            self.record_btn.setText("Stop Recording")
            self.record_btn.setIcon(FIF.PAUSE.icon())
            self.start_recording.emit()
        else:
            self.status_icon.setText("⚫")
            self.status_label.setText("Processing...")
            self.record_btn.setText("Start Recording")
            self.record_btn.setIcon(FIF.MICROPHONE.icon())
            self.stop_recording.emit()
            # Note: Actual transcription result will come from app via signal
            # The _show_result() is only for standalone testing
            
    def append_transcription(self, text: str):
        """Add transcription result to output (called by main window)."""
        self.output_text.append(text)
        self.status_label.setText("Ready")
    
    def _show_result(self):
        """Simulated result for testing only."""
        self.status_label.setText("Ready")
        self.output_text.append("[Test Mode] This is a simulated transcription result. ")

    # ==================== Insights & History ====================

    def update_summary(self, summary: Any):
        """Update summary metrics shown at the top of the page."""
        total = self._get_summary_value(summary, "total_transcriptions")
        avg_words = 0
        avg_duration = 0
        avg_conf = self._get_summary_value(summary, "average_confidence")

        if total > 0:
            total_words = self._get_summary_value(summary, "total_words")
            total_duration = self._get_summary_value(summary, "total_audio_duration")
            avg_words = total_words / total if total_words else 0
            avg_duration = total_duration / total if total_duration else 0

        self.summary_labels["total"].setText(str(int(total)))
        self.summary_labels["avg_words"].setText(f"{avg_words:.1f}")
        self.summary_labels["avg_duration"].setText(f"{avg_duration:.1f}s")
        if avg_conf:
            self.summary_labels["avg_confidence"].setText(f"{avg_conf*100:.0f}%")
        else:
            self.summary_labels["avg_confidence"].setText("—")

    def add_history_entry(self, entry: Dict[str, Any]):
        """Append a transcription history entry with metadata."""
        if not entry:
            return

        item = QListWidgetItem(self._format_history_entry(entry))
        item.setData(Qt.ItemDataRole.UserRole, entry)
        self.history_list.addItem(item)

        # Limit to last 50 entries
        if self.history_list.count() > 50:
            self.history_list.takeItem(0)

        self.history_list.scrollToBottom()

    def _on_history_selected(self, item: QListWidgetItem):
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry and entry.get("text"):
            self.output_text.setPlainText(entry["text"])

    def _format_history_entry(self, entry: Dict[str, Any]) -> str:
        timestamp = entry.get("timestamp")
        if hasattr(timestamp, "strftime"):
            timestamp_str = timestamp.strftime("%H:%M:%S")
        else:
            timestamp_str = str(timestamp)

        app = entry.get("application") or "Unknown app"
        duration = entry.get("audio_duration") or 0
        words = entry.get("word_count") or 0
        characters = entry.get("character_count") or 0
        confidence = entry.get("confidence")
        confidence_str = f"{confidence*100:.0f}%" if confidence is not None else "—"
        preview = (entry.get("text") or "").strip()
        if len(preview) > 120:
            preview = preview[:117] + "..."

        return (
            f"{timestamp_str} • {app}\n"
            f"{duration:.1f}s • {words} words / {characters} chars • Conf {confidence_str}\n"
            f"{preview}"
        )

    @staticmethod
    def _get_summary_value(summary: Any, attr: str) -> float:
        if hasattr(summary, attr):
            return getattr(summary, attr)
        if isinstance(summary, dict):
            return summary.get(attr, 0)
        return 0

    def set_audio_level(self, level: float):
        """Update VU meter."""
        if hasattr(self, "level_bar"):
            self.level_bar.setValue(int(min(1.0, max(0.0, level)) * 100))
