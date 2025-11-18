"""
Recording Widget - Floating status indicator with waveform animation and timer

Inspired by whisper-flow's elegant design
"""

from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QApplication
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath, QFont
from qfluentwidgets import IconWidget, FluentIcon as FIF, BodyLabel, CaptionLabel
import math
import random

from ..branding import (
    COLOR_RECORDING, COLOR_PROCESSING, COLOR_READY,
    FONT_SIZE_SMALL, FONT_SIZE_CAPTION,
    FONT_WEIGHT_BOLD, FONT_WEIGHT_NORMAL,
    RADIUS_MD, SPACING_XS,
    ICON_MICROPHONE
)


class WaveformWidget(QWidget):
    """Animated waveform display with real audio level input"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(30)
        
        # Waveform bars - store recent audio levels
        self.num_bars = 32  # More bars for smoother visual
        self.bar_heights = [0.2] * self.num_bars
        self.target_heights = [0.2] * self.num_bars
        self.audio_levels = []  # Recent audio levels for display
        
        # Animation state
        self.recording = False
        self.transcribing = False
        self.frame_count = 0
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_waveform)
        self.timer.setInterval(50)  # 20 FPS
    
    def update_audio_level(self, level: float):
        """Update with real audio level from recording (0.0 to 1.0)"""
        if self.recording:
            # Store level
            self.audio_levels.append(level)
            if len(self.audio_levels) > self.num_bars:
                self.audio_levels.pop(0)
            
            # Update bars based on audio level
            for i in range(len(self.audio_levels)):
                idx = self.num_bars - len(self.audio_levels) + i
                if idx >= 0:
                    # Scale audio level for visual effect
                    self.target_heights[idx] = 0.1 + self.audio_levels[i] * 0.8
    
    def start_recording(self):
        """Start recording animation with active waveform"""
        self.recording = True
        self.transcribing = False
        self.frame_count = 0
        self.audio_levels = []
        if not self.timer.isActive():
            self.timer.start()
    
    def start_transcribing(self):
        """Start transcribing animation with pulsing effect"""
        self.recording = False
        self.transcribing = True
        self.frame_count = 0
        if not self.timer.isActive():
            self.timer.start()
    
    def stop(self):
        """Stop all animation"""
        self.recording = False
        self.transcribing = False
        self.timer.stop()
        self.audio_levels = []
        # Smooth fade to baseline
        for i in range(self.num_bars):
            self.target_heights[i] = 0.1
        self.update()
    
    def _update_waveform(self):
        """Update waveform animation"""
        self.frame_count += 1
        
        if self.transcribing:
            # Pulsing animation for transcription
            pulse = (math.sin(self.frame_count * 0.05) + 1) / 2
            for i in range(self.num_bars):
                # Center bars pulse more
                center_weight = 1 - abs(i - self.num_bars / 2) / (self.num_bars / 2)
                self.target_heights[i] = 0.1 + pulse * center_weight * 0.5
        elif not self.recording:
            # Idle state - gentle baseline
            for i in range(self.num_bars):
                self.target_heights[i] = 0.1
        
        # Smooth interpolation
        for i in range(self.num_bars):
            self.bar_heights[i] += (self.target_heights[i] - self.bar_heights[i]) * 0.3
        
        self.update()
    
    def paintEvent(self, event):
        """Draw waveform bars"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Colors - brighter and more prominent
        if self.recording:
            color = QColor("#FF5252")  # Bright red for recording
            glow_color = QColor("#FF5252")
            glow_color.setAlpha(50)
        elif self.transcribing:
            color = QColor("#00BCD4")  # Bright cyan for transcribing
            glow_color = QColor("#00BCD4")
            glow_color.setAlpha(50)
        else:
            color = QColor("#4CAF50")  # Bright green for idle
            glow_color = QColor("#4CAF50")
            glow_color.setAlpha(50)
        
        # Calculate bar dimensions with padding
        padding = 4
        available_width = self.width() - (padding * 2)
        bar_spacing = 3
        total_spacing = bar_spacing * (self.num_bars - 1)
        bar_width = (available_width - total_spacing) / self.num_bars
        
        # Draw bars with glow effect
        for i in range(self.num_bars):
            height = max(3, int(self.height() * self.bar_heights[i]))
            x = padding + i * (bar_width + bar_spacing)
            y = (self.height() - height) // 2
            
            # Draw glow background
            painter.fillRect(int(x - 1), y - 1, int(bar_width + 2), height + 2, glow_color)
            
            # Draw main bar
            painter.fillRect(int(x), y, int(bar_width), height, color)


class RecordingWidget(QWidget):
    """
    Floating recording status widget with waveform
    
    States:
    - Hidden: Not recording
    - Recording: Red dot + waveform + timer
    - Transcribing: Cyan pulse + "Processing..."
    """
    
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # State
        self.recording_time = 0
        self.is_recording = False
        self.is_transcribing = False
        
        # Setup UI
        self._setup_ui()
        
        # Timer for recording duration
        self.duration_timer = QTimer(self)
        self.duration_timer.timeout.connect(self._update_duration)
        self.duration_timer.setInterval(100)  # Update every 100ms
        
        # Fade animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        
        # Start hidden
        self.hide()
    
    def _setup_ui(self):
        """Setup the widget UI with modern design system"""
        self.setFixedSize(160, 44)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Status icon
        self.status_icon = IconWidget(ICON_MICROPHONE, self)
        self.status_icon.setFixedSize(20, 20)

        # Status label
        self.status_label = QLabel("Recording")
        self.status_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_SMALL}px;
            font-weight: {FONT_WEIGHT_BOLD};
            color: #FFFFFF;
            background: transparent;
        """)

        # Timer label
        self.timer_label = QLabel("0.0s")
        self.timer_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_CAPTION}px;
            font-weight: {FONT_WEIGHT_NORMAL};
            color: #CCCCCC;
            background: transparent;
        """)

        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.timer_label)

        # Modern background with design system
        self.setStyleSheet(f"""
            RecordingWidget {{
                background: rgba(45, 45, 45, 240);
                border-radius: {RADIUS_MD}px;
                border: 1px solid rgba(103, 81, 161, 150);
            }}
        """)
    
    def start_recording(self):
        """Start recording state"""
        self.is_recording = True
        self.is_transcribing = False
        self.recording_time = 0

        # Update UI
        self.status_label.setText("Recording")
        self.status_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_SMALL}px;
            font-weight: {FONT_WEIGHT_BOLD};
            color: {COLOR_RECORDING};
            background: transparent;
        """)
        self.timer_label.setText("0.0s")

        # Start duration timer
        if not self.duration_timer.isActive():
            self.duration_timer.start()

        # Fade in
        self._fade_in()
    
    def start_transcribing(self):
        """Start transcribing state"""
        self.is_recording = False
        self.is_transcribing = True

        # Stop duration timer if active
        if self.duration_timer.isActive():
            self.duration_timer.stop()

        # Update UI
        self.status_label.setText("Processing")
        self.status_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_SMALL}px;
            font-weight: {FONT_WEIGHT_BOLD};
            color: {COLOR_PROCESSING};
            background: transparent;
        """)
        self.timer_label.setText(f"{self.recording_time:.1f}s")
    
    def finish(self):
        """Finish and hide widget"""
        self.is_recording = False
        self.is_transcribing = False
        
        # Stop timers safely
        if self.duration_timer.isActive():
            self.duration_timer.stop()
        
        # Fade out
        self._fade_out()
    
    def _update_duration(self):
        """Update recording duration display"""
        self.recording_time += 0.1
        self.timer_label.setText(f"{self.recording_time:.1f}s")
    
    def _fade_in(self):
        """Fade in animation"""
        self.show()
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
    
    def _fade_out(self):
        """Fade out animation"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
    
    def position_at_bottom_right(self, parent_widget):
        """Position widget at bottom-right of parent"""
        # Use screen geometry instead of parent geometry for floating widget
        try:
            # Try modern Qt API first (Qt 5.10+)
            screen = QApplication.screenAt(parent_widget.geometry().center())
            if not screen:
                screen = QApplication.primaryScreen()
            screen_rect = screen.availableGeometry()
        except AttributeError:
            # Fallback to deprecated API for older Qt versions
            screen_rect = QApplication.desktop().availableGeometry(parent_widget)

        x = screen_rect.right() - self.width() - 20
        y = screen_rect.bottom() - self.height() - 80  # Above taskbar
        self.move(x, y)
