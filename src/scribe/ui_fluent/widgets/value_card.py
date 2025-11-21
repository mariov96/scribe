"""
Value Card Widget
Displays a metric with icon, title, value, and trend
"""

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QGraphicsOpacityEffect
from qfluentwidgets import CardWidget, TitleLabel, BodyLabel, CaptionLabel, FluentIcon as FIF, isDarkTheme

from ..branding import get_secondary_color


class ValueCard(CardWidget):
    """Card showing a metric value with update capability"""
    
    def __init__(self, icon: FIF, title: str, value: str, 
                 subtitle: str = "", trend: str = "", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon + Title
        header = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(icon.icon().pixmap(24, 24))
        title_label = BodyLabel(title)
        is_dark = isDarkTheme()
        title_label.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()
        
        # Big value
        self.value_label = TitleLabel(value)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Make value larger
        font = self.value_label.font()
        font.setPointSize(24)
        font.setBold(True)
        self.value_label.setFont(font)
        
        # Subtitle
        self.sub_label = None
        if subtitle:
            self.sub_label = BodyLabel(subtitle)
            self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sub_label.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        
        # Trend
        self.trend_label = None
        if trend:
            self.trend_label = CaptionLabel(trend)
            self.trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._set_trend_color(trend)
        
        layout.addLayout(header)
        layout.addWidget(self.value_label)
        if self.sub_label:
            layout.addWidget(self.sub_label)
        if self.trend_label:
            layout.addWidget(self.trend_label)
        
        self.setFixedSize(200, 160)

    def set_value(self, value: str, animate: bool = True):
        """Update the value displayed on the card"""
        if self.value_label.text() == value:
            return
            
        if animate:
            # Fade out/in animation
            effect = QGraphicsOpacityEffect(self.value_label)
            self.value_label.setGraphicsEffect(effect)
            
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(200)
            anim.setStartValue(0.5)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutQuad)
            anim.start()
            self._anim = anim # Keep reference
            
        self.value_label.setText(value)

    def set_trend(self, trend: str):
        """Update the trend text"""
        if self.trend_label:
            self.trend_label.setText(trend)
            self._set_trend_color(trend)

    def _set_trend_color(self, trend: str):
        if "↑" in trend:
            self.trend_label.setTextColor(QColor(82, 196, 26), QColor(82, 196, 26))
        elif "↓" in trend:
            self.trend_label.setTextColor(QColor(245, 34, 45), QColor(245, 34, 45))
