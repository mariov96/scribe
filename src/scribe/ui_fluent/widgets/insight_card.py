"""
Insight Card Widget
Displays analytics insights from usage data
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import CardWidget, SubtitleLabel, BodyLabel, StrongBodyLabel, isDarkTheme

from ..branding import SCRIBE_PURPLE, get_contrasting_color


class InsightCard(CardWidget):
    """Card showing an interesting insight from usage data"""
    
    def __init__(self, icon_text: str, title: str, insight: str, 
                 metric: str = "", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with icon
        header = QHBoxLayout()
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("font-size: 32px;")
        title_label = SubtitleLabel(title)
        
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()
        
        # Insight text
        insight_label = BodyLabel(insight)
        insight_label.setWordWrap(True)
        is_dark = isDarkTheme()
        insight_label.setTextColor(get_contrasting_color(is_dark), get_contrasting_color(is_dark))
        
        # Metric (if provided)
        if metric:
            metric_label = StrongBodyLabel(metric)
            metric_label.setTextColor(QColor(SCRIBE_PURPLE), QColor(SCRIBE_PURPLE))
            layout.addWidget(metric_label)
        
        layout.addLayout(header)
        layout.addWidget(insight_label)
        
        self.setFixedHeight(180)
