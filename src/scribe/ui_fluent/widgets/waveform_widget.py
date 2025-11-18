"""
Real-time audio waveform visualization widget
"""

import logging
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient

logger = logging.getLogger(__name__)


class WaveformWidget(QWidget):
    """
    Real-time audio waveform visualization
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setMinimumWidth(300)
        
        # Audio level history (last 50 samples)
        self.levels = [0.0] * 50
        self.max_level = 0.0
        
        # Animation
        self.animation_value = 0.0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(50)  # 20 FPS
    
    def update_level(self, level: float):
        """Update with new audio level (0.0 to 1.0)"""
        # Shift left and add new level
        self.levels = self.levels[1:] + [level]
        self.max_level = max(self.levels)
        self.update()
    
    def reset(self):
        """Reset waveform to zero"""
        self.levels = [0.0] * 50
        self.max_level = 0.0
        self.update()
    
    def _animate(self):
        """Animate the waveform"""
        self.animation_value = (self.animation_value + 0.05) % 1.0
        self.update()
    
    def paintEvent(self, event):
        """Draw the dramatic waveform with neon effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Deep dark background
        painter.fillRect(self.rect(), QColor(10, 10, 15, 240))
        
        # Draw waveform bars with neon glow
        width = self.width()
        height = self.height()
        bar_width = width / len(self.levels)
        
        # Vibrant purple-pink gradient (neon style)
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(186, 85, 211, 250))  # Medium orchid
        gradient.setColorAt(0.3, QColor(138, 43, 226, 240))  # Blue violet
        gradient.setColorAt(0.7, QColor(103, 81, 161, 220))  # SCRIBE_PURPLE
        gradient.setColorAt(1, QColor(75, 0, 130, 200))  # Indigo
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        
        for i, level in enumerate(self.levels):
            if level > 0.01:  # Only draw visible bars
                x = i * bar_width
                bar_height = level * height * 0.9  # 90% of widget height max
                y = (height - bar_height) / 2
                
                # Add dramatic animation effect
                animation_offset = abs(i - len(self.levels) * self.animation_value) / len(self.levels)
                scale = 0.8 + 0.2 * (1 - animation_offset)
                bar_height *= scale
                y = (height - bar_height) / 2
                
                # Draw outer glow (larger, more transparent)
                painter.setOpacity(0.15)
                painter.drawRoundedRect(QRectF(x - 3, y - 4, bar_width + 4, bar_height + 8), 4, 4)
                
                # Draw mid glow
                painter.setOpacity(0.35)
                painter.drawRoundedRect(QRectF(x - 1, y - 2, bar_width + 1, bar_height + 4), 3, 3)
                
                # Draw solid bar
                painter.setOpacity(1.0)
                painter.drawRoundedRect(QRectF(x, y, bar_width - 2, bar_height), 3, 3)
        
        # Draw neon center line with glow
        painter.setOpacity(0.4)
        glow_pen = QPen(QColor(138, 43, 226, 150), 3)
        painter.setPen(glow_pen)
        painter.drawLine(0, height // 2, width, height // 2)
        
        painter.setOpacity(1.0)
        painter.setPen(QPen(QColor(186, 85, 211, 200), 1))
        painter.drawLine(0, height // 2, width, height // 2)
