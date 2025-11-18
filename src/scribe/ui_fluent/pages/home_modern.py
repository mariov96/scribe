"""
Modern Dashboard Home Page
Shows at-a-glance stats, recent activity, and quick actions
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QSizePolicy, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QFont, QColor, QPainter, QPen
from qfluentwidgets import (
    ScrollArea, CardWidget, IconWidget, BodyLabel, CaptionLabel,
    TitleLabel, SubtitleLabel, PrimaryPushButton, PushButton,
    FluentIcon as FIF, InfoBar, InfoBarPosition, ProgressRing,
    setTheme, Theme, isDarkTheme
)

logger = logging.getLogger(__name__)


class StatCard(CardWidget):
    """
    Simple stat card
    """
    def __init__(self, icon: FIF, title: str, value: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        
        # Value (prominent)
        self.value_label = TitleLabel(value, self)
        font = self.value_label.font()
        font.setPointSize(22)
        font.setBold(True)
        self.value_label.setFont(font)
        layout.addWidget(self.value_label)
        
        # Title (plain)
        self.title_label = BodyLabel(title, self)
        layout.addWidget(self.title_label)
        
        # Subtitle (optional)
        if subtitle:
            self.subtitle_label = CaptionLabel(subtitle, self)
            # rely on theme defaults for color
            layout.addWidget(self.subtitle_label)
        
        layout.addStretch()
    
    def update_value(self, value: str, animate: bool = True):
        """Update the stat value with optional animation"""
        if animate:
            # Add pulse animation
            effect = QGraphicsOpacityEffect(self.value_label)
            self.value_label.setGraphicsEffect(effect)
            
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(300)
            animation.setStartValue(0.3)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.InOutQuad)
            animation.start()
            
            # Keep reference to prevent garbage collection
            self._animation = animation
        
        self.value_label.setText(value)


class RecentActivityCard(CardWidget):
    """
    Card showing a recent transcription with preview
    """
    clicked = pyqtSignal(int)  # Emits transcription ID
    
    def __init__(self, transcription_id: int, text: str, app_name: str, 
                 timestamp: datetime, confidence: float, parent=None):
        super().__init__(parent)
        self.transcription_id = transcription_id
        self.setFixedHeight(100)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)
        
        # Minimal look
        self.setStyleSheet("""
            RecentActivityCard {
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
            }
            RecentActivityCard:hover {
                background-color: rgba(255, 255, 255, 0.03);
            }
        """)
        
        # Top row: app name and timestamp with icons
        top_layout = QHBoxLayout()
        
        # App icon
        app_icon = IconWidget(FIF.APPLICATION, self)
        app_icon.setFixedSize(16, 16)
        top_layout.addWidget(app_icon)
        
        app_label = BodyLabel(app_name, self)
        top_layout.addWidget(app_label)
        
        top_layout.addStretch()
        
        # Time with clock icon
        time_icon = IconWidget(FIF.HISTORY, self)
        time_icon.setFixedSize(14, 14)
        top_layout.addWidget(time_icon)
        
        time_label = CaptionLabel(self._format_timestamp(timestamp), self)
        top_layout.addWidget(time_label)
        
        layout.addLayout(top_layout)
        
        # Text preview
        preview = text[:90] + "..." if len(text) > 90 else text
        text_label = BodyLabel(preview, self)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)
        
        # Bottom row: confidence indicator with visual bar
        if confidence is not None and confidence > 0:
            bottom_layout = QHBoxLayout()
            
            # Confidence bar (visual indicator)
            confidence_bar = QWidget(self)
            bar_width = int(confidence * 100)
            confidence_bar.setFixedSize(bar_width, 4)
            confidence_bar.setStyleSheet("background-color: rgba(138, 43, 226, 0.8); border-radius: 2px;")
            bottom_layout.addWidget(confidence_bar)
            
            confidence_label = CaptionLabel(f"{confidence:.0%} accurate", self)
            bottom_layout.addWidget(confidence_label)
            bottom_layout.addStretch()
            
            layout.addLayout(bottom_layout)
    
    def _format_timestamp(self, dt: datetime) -> str:
        """Format timestamp relative to now"""
        now = datetime.now()
        delta = now - dt
        
        if delta < timedelta(minutes=1):
            return "Just now"
        elif delta < timedelta(hours=1):
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m ago"
        elif delta < timedelta(days=1):
            hours = int(delta.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            return dt.strftime("%b %d, %I:%M %p")
    
    def mousePressEvent(self, event):
        """Handle click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.transcription_id)
        super().mousePressEvent(event)


class QuickActionCard(CardWidget):
    """
    Simple action card
    """
    clicked = pyqtSignal()
    
    def __init__(self, icon: FIF, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 100)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon
        icon_widget = IconWidget(icon, self)
        icon_widget.setFixedSize(24, 24)
        layout.addWidget(icon_widget, 0, Qt.AlignCenter)
        
        # Title
        title_label = BodyLabel(title, self)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = CaptionLabel(subtitle, self)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setTextColor(QColor(120, 120, 120), QColor(120, 120, 120))
        layout.addWidget(subtitle_label)
    
    def mousePressEvent(self, event):
        """Handle click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ModernHomePage(ScrollArea):
    """
    Modern dashboard home page with stats, activity, and quick actions
    """
    
    # Signals
    start_recording_clicked = pyqtSignal()
    view_history_clicked = pyqtSignal()
    view_insights_clicked = pyqtSignal()
    transcription_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ModernHomePage")
        self.setWidgetResizable(True)
        
        # Stats cache
        self.total_transcriptions = 0
        self.words_saved = 0
        self.time_saved_seconds = 0
        self.recent_transcriptions = []
        
        self._setup_ui()
        self._setup_refresh_timer()
        
        logger.info("Modern home page initialized")
    
    def _setup_ui(self):
        """Setup the UI"""
        # Main container
        container = QWidget()
        container.setObjectName("homePageContainer")
        self.setWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)
        
        # Welcome header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        welcome_label = TitleLabel("Welcome to Scribe", self)
        font = welcome_label.font()
        font.setPointSize(28)
        welcome_label.setFont(font)
        header_layout.addWidget(welcome_label)
        
        subtitle_label = BodyLabel("Your AI-powered transcription assistant", self)
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Stats cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.transcriptions_card = StatCard(
            FIF.DOCUMENT,
            "Transcriptions Today",
            "0",
            parent=self
        )
        stats_layout.addWidget(self.transcriptions_card)
        
        self.words_card = StatCard(
            FIF.EDIT,
            "Words Saved",
            "0",
            "Total typed for you",
            parent=self
        )
        stats_layout.addWidget(self.words_card)
        
        self.time_card = StatCard(
            FIF.HISTORY,
            "Time Saved",
            "0m",
            "Estimated typing time",
            parent=self
        )
        stats_layout.addWidget(self.time_card)
        
        layout.addLayout(stats_layout)
        
        # Quick actions section (no header to avoid duplication)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)
        
        self.record_card = QuickActionCard(
            FIF.MICROPHONE,
            "Start Recording",
            "Press Ctrl+Alt to begin",
            parent=self
        )
        self.record_card.clicked.connect(self.start_recording_clicked)
        actions_layout.addWidget(self.record_card)
        
        self.history_card = QuickActionCard(
            FIF.HISTORY,
            "View History",
            "Browse past transcriptions",
            parent=self
        )
        self.history_card.clicked.connect(self.view_history_clicked)
        actions_layout.addWidget(self.history_card)
        
        self.insights_card = QuickActionCard(
            FIF.INFO,
            "View Insights",
            "See your productivity stats",
            parent=self
        )
        self.insights_card.clicked.connect(self.view_insights_clicked)
        actions_layout.addWidget(self.insights_card)
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        # Recent activity section
        activity_label = SubtitleLabel("Recent Activity", self)
        layout.addWidget(activity_label)
        
        self.activity_container = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setSpacing(12)
        self.activity_layout.setContentsMargins(0, 0, 0, 0)
        
        # Placeholder when no activity
        self.no_activity_label = BodyLabel("No recent transcriptions. Start recording to see your activity here!", self)
        self.activity_layout.addWidget(self.no_activity_label)
        
        layout.addWidget(self.activity_container)
        
        layout.addStretch()
    
    def _setup_refresh_timer(self):
        """Setup timer to refresh stats periodically"""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def refresh_stats(self):
        """Refresh statistics from the database"""
        try:
            # Update stat cards
            self.transcriptions_card.update_value(str(self.total_transcriptions))
            self.words_card.update_value(f"{self.words_saved:,}")
            
            # Format time saved
            minutes = self.time_saved_seconds // 60
            if minutes < 60:
                time_str = f"{minutes}m"
            else:
                hours = minutes // 60
                time_str = f"{hours}h {minutes % 60}m"
            self.time_card.update_value(time_str)
            
            # Update recent activity
            self._update_recent_activity()
            
        except Exception as e:
            logger.error(f"Error refreshing stats: {e}", exc_info=True)
    
    def _update_recent_activity(self):
        """Update recent activity cards"""
        # Clear existing cards
        while self.activity_layout.count() > 0:
            item = self.activity_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.recent_transcriptions:
            # Show placeholder
            self.no_activity_label = BodyLabel("No recent transcriptions. Start recording to see your activity here!", self)
            self.activity_layout.addWidget(self.no_activity_label)
        else:
            # Show recent transcription cards (max 5)
            for trans in self.recent_transcriptions[:5]:
                card = RecentActivityCard(
                    transcription_id=trans.get('id', 0),
                    text=trans.get('text', ''),
                    app_name=trans.get('application', 'Unknown'),
                    timestamp=trans.get('timestamp', datetime.now()),
                    confidence=trans.get('confidence', 0.0),
                    parent=self
                )
                card.clicked.connect(self.transcription_clicked)
                self.activity_layout.addWidget(card)
    
    def update_stats(self, total_transcriptions: int, words_saved: int, time_saved_seconds: int):
        """Update statistics"""
        self.total_transcriptions = total_transcriptions
        self.words_saved = words_saved
        self.time_saved_seconds = time_saved_seconds
        self.refresh_stats()
    
    def update_recent_activity(self, transcriptions: List[Dict]):
        """Update recent transcriptions list"""
        self.recent_transcriptions = transcriptions
        self._update_recent_activity()
