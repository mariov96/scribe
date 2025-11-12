"""
Value Card Widget
Displays a metric with icon, title, value, and trend
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import CardWidget, TitleLabel, BodyLabel, CaptionLabel, FluentIcon as FIF, isDarkTheme

from ..branding import get_secondary_color


class ValueCard(CardWidget):
    """Card showing a metric value"""
    
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
        value_label = TitleLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        if subtitle:
            sub_label = BodyLabel(subtitle)
            sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub_label.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        
        # Trend
        if trend:
            trend_label = CaptionLabel(trend)
            trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if "↑" in trend:
                trend_label.setTextColor(QColor(82, 196, 26), QColor(82, 196, 26))
            elif "↓" in trend:
                trend_label.setTextColor(QColor(245, 34, 45), QColor(245, 34, 45))
        
        layout.addLayout(header)
        layout.addWidget(value_label)
        if subtitle:
            layout.addWidget(sub_label)
        if trend:
            layout.addWidget(trend_label)
        
        self.setFixedSize(200, 160)
