"""
Transcription Page - Main recording interface
"""

from PyQt5.QtCore import pyqtSignal as Signal, QTimer, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from typing import Any, Dict, Optional
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel,
    CardWidget, PrimaryPushButton, PushButton, ComboBox, TextEdit,
    FluentIcon as FIF, IconWidget, StrongBodyLabel, isDarkTheme
)
from ..widgets import ValueCard
from ..branding import get_secondary_color

class TranscriptionPage(ScrollArea):
    """Main transcription interface"""
    
    start_recording = Signal()
    stop_recording = Signal()
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.setObjectName("TranscriptionPage")
        self.config_manager = config_manager
        
        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        
        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(24)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        title = TitleLabel("Transcription")
        subtitle = BodyLabel("Record and transcribe audio in real-time")
        is_dark = isDarkTheme()
        subtitle.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self.vBoxLayout.addLayout(header_layout)
        
        # Main Controls Card
        self.control_card = self._create_controls()
        self.vBoxLayout.addWidget(self.control_card)
        
        # Output Section
        output_label = SubtitleLabel("Live Output")
        self.output_text = TextEdit()
        self.output_text.setPlaceholderText("Transcribed text will appear here...")
        self.output_text.setMinimumHeight(200)
        # Modern styling for text edit
        self.output_text.setStyleSheet("""
            TextEdit {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                line-height: 1.5;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.03);
            }
        """)
        
        self.vBoxLayout.addWidget(output_label)
        self.vBoxLayout.addWidget(self.output_text)
        
        # Metrics Section
        metrics_label = SubtitleLabel("Session Metrics")
        self.metrics_layout = QHBoxLayout()
        self.metrics_layout.setSpacing(16)
        
        self.metric_words = ValueCard(FIF.EDIT, "Words", "0", "Total words")
        self.metric_duration = ValueCard(FIF.HISTORY, "Duration", "0s", "Total time")
        self.metric_confidence = ValueCard(FIF.CERTIFICATE, "Accuracy", "—", "Avg confidence")
        
        self.metrics_layout.addWidget(self.metric_words)
        self.metrics_layout.addWidget(self.metric_duration)
        self.metrics_layout.addWidget(self.metric_confidence)
        self.metrics_layout.addStretch()
        
        self.vBoxLayout.addWidget(metrics_label)
        self.vBoxLayout.addLayout(self.metrics_layout)
        
        self.vBoxLayout.addStretch(1)
        
        self.recording = False

    def _create_controls(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Top Row: Status and Level
        status_row = QHBoxLayout()
        
        # Status Indicator
        self.status_container = QWidget()
        status_layout = QHBoxLayout(self.status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(12)
        
        self.status_icon = IconWidget(FIF.MICROPHONE)
        self.status_icon.setFixedSize(24, 24)
        
        status_text_layout = QVBoxLayout()
        status_text_layout.setSpacing(2)
        self.status_title = StrongBodyLabel("Ready")
        self.status_desc = CaptionLabel("Press record to start")
        is_dark = isDarkTheme()
        self.status_desc.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        
        status_text_layout.addWidget(self.status_title)
        status_text_layout.addWidget(self.status_desc)
        
        status_layout.addWidget(self.status_icon)
        status_layout.addLayout(status_text_layout)
        
        # Level Meter
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        self.level_bar.setTextVisible(False)
        self.level_bar.setFixedWidth(200)
        self.level_bar.setFixedHeight(6)
        self.level_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: rgba(255, 255, 255, 0.1);
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        status_row.addWidget(self.status_container)
        status_row.addStretch()
        status_row.addWidget(self.level_bar)
        
        # Middle Row: Settings
        settings_row = QHBoxLayout()
        settings_row.setSpacing(16)
        
        # Language
        lang_container = QVBoxLayout()
        lang_container.setSpacing(4)
        lang_label = CaptionLabel("Language")
        lang_label.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        self.lang_combo = ComboBox()
        self.lang_combo.addItems(["Auto-detect", "English", "Spanish", "French", "German", "Chinese", "Japanese"])
        self.lang_combo.setFixedWidth(160)
        lang_container.addWidget(lang_label)
        lang_container.addWidget(self.lang_combo)
        
        # Model
        model_container = QVBoxLayout()
        model_container.setSpacing(4)
        model_label = CaptionLabel("Model")
        model_label.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        self.model_combo = ComboBox()
        self.model_combo.addItems(["Base", "Small", "Medium", "Large-v3"])
        self.model_combo.setCurrentIndex(1) # Default to Small
        self.model_combo.setFixedWidth(160)
        model_container.addWidget(model_label)
        model_container.addWidget(self.model_combo)
        
        settings_row.addLayout(lang_container)
        settings_row.addLayout(model_container)
        settings_row.addStretch()
        
        # Bottom Row: Action Button
        action_row = QHBoxLayout()
        self.record_btn = PrimaryPushButton(FIF.MICROPHONE, "Start Recording")
        self.record_btn.setFixedSize(200, 48)
        self.record_btn.clicked.connect(self._toggle_recording)
        
        action_row.addStretch()
        action_row.addWidget(self.record_btn)
        action_row.addStretch()
        
        layout.addLayout(status_row)
        layout.addSpacing(8)
        layout.addLayout(settings_row)
        layout.addSpacing(16)
        layout.addLayout(action_row)
        
        return card

    def _toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.status_icon.setIcon(FIF.STOP)
            self.status_title.setText("Recording")
            self.status_title.setStyleSheet("color: #FF4D4F;")
            self.status_desc.setText("Listening...")
            self.record_btn.setText("Stop Recording")
            self.record_btn.setIcon(FIF.STOP)
            self.start_recording.emit()
        else:
            self.status_icon.setIcon(FIF.MICROPHONE)
            self.status_title.setText("Ready")
            self.status_title.setStyleSheet("")
            self.status_desc.setText("Press record to start")
            self.record_btn.setText("Start Recording")
            self.record_btn.setIcon(FIF.MICROPHONE)
            self.stop_recording.emit()

    def append_transcription(self, text: str):
        """Add transcription result to output."""
        self.output_text.append(text)
        
    def set_audio_level(self, level: float):
        """Update VU meter."""
        if hasattr(self, "level_bar"):
            self.level_bar.setValue(int(min(1.0, max(0.0, level)) * 100))
            
    def update_metrics(self, words: int, duration: float, confidence: float):
        """Update session metrics."""
        self.metric_words.set_value(str(words))
        
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        self.metric_duration.set_value(f"{minutes}m {seconds}s")
        
        if confidence > 0:
            self.metric_confidence.set_value(f"{confidence*100:.0f}%")
