"""
Home Page - Modern dashboard with stats, activity, and quick actions
"""

from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QTimer, pyqtSignal as Signal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel,
    CardWidget, PrimaryPushButton, PushButton, FlowLayout,
    FluentIcon as FIF, isDarkTheme, IconWidget, TextEdit,
    StrongBodyLabel
)

from ..branding import (
    # Design system imports
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL,
    CARD_PADDING, SECTION_SPACING, PAGE_MARGIN,
    FONT_SIZE_HERO, FONT_SIZE_H2, FONT_SIZE_BODY, FONT_SIZE_SMALL, FONT_SIZE_CAPTION,
    FONT_WEIGHT_BOLD, FONT_WEIGHT_SEMIBOLD, FONT_WEIGHT_MEDIUM, FONT_WEIGHT_NORMAL,
    COLOR_READY, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_TERTIARY,
    COLOR_BG_TERTIARY, RADIUS_MD, RADIUS_LG,
    ICON_MICROPHONE, ICON_HOTKEY, ICON_SPEED, ICON_PRIVACY,
    ICON_TEST, ICON_PLAY, ICON_SUCCESS, ICON_WARNING,
    SCRIBE_PURPLE
)
from ..widgets import ValueCard
from .home_modern import StatCard, RecentActivityCard, QuickActionCard


class HomePage(ScrollArea):
    """Modern home dashboard with crisp design"""

    # Signals for button actions
    start_listening_clicked = Signal()
    stop_recording_clicked = Signal()
    test_audio_clicked = Signal()
    settings_clicked = Signal()
    view_history_clicked = Signal()
    view_insights_clicked = Signal()
    transcription_clicked = Signal(int)

    def __init__(self, value_calculator=None, parent=None):
        super().__init__(parent)
        self.setObjectName("HomePage")

        self.value_calculator = value_calculator
        
        # Stats cache for modern dashboard
        self.total_transcriptions = 0
        self.words_saved = 0
        self.time_saved_seconds = 0
        self.recent_transcriptions = []

        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN)
        self.vBoxLayout.setSpacing(SPACING_LG)

        # Welcome greeting
        welcome_section = self._create_welcome_section()
        self.vBoxLayout.addWidget(welcome_section)
        
        # Modern stats cards
        stats_section = self._create_stats_section()
        self.vBoxLayout.addWidget(stats_section)
        
        # Quick actions
        actions_section = self._create_quick_actions()
        self.vBoxLayout.addWidget(actions_section)
        
        # Recent activity
        activity_section = self._create_recent_activity()
        self.vBoxLayout.addWidget(activity_section)

        # Status card with modern design (hidden by default - replaced by modern UI)
        status_card = self._create_status_card()
        status_card.hide()  # Hide old status card
        self.vBoxLayout.addWidget(status_card)

        # Test transcription area (hidden - for testing only)
        test_card = self._create_test_transcription()
        test_card.hide()  # Hide test card
        self.vBoxLayout.addWidget(test_card)
        
        self.vBoxLayout.addStretch(1)

        # Store metric cards for updates
        self.time_card = None
        self.words_card = None
        self.accuracy_card = None
        self.commands_card = None

        # Force an initial relayout/repaint to avoid any stale paint until scroll
        QTimer.singleShot(0, self._refresh_first_paint)

    def showEvent(self, event):
        super().showEvent(event)
        # Ensure a clean layout/paint right after the page is shown
        QTimer.singleShot(0, self._refresh_first_paint)

    def _refresh_first_paint(self):
        try:
            # Activate layouts and repaint the scroll viewport
            if self.view.layout():
                self.view.layout().activate()
            self.view.updateGeometry()
            self.view.adjustSize()
            self.view.repaint()
            if self.viewport():
                self.viewport().update()
        except Exception:
            pass

    def _create_status_card(self):
        """Create DRAMATIC hero status card - unmistakable modern design"""
        card = CardWidget()

        # DRAMATIC purple gradient background with shadow
        card.setStyleSheet(f"""
            CardWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {SCRIBE_PURPLE}, stop:1 #4A3880);
                border: 2px solid {SCRIBE_PURPLE};
                border-radius: {RADIUS_LG}px;
                padding: 24px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(SPACING_LG)

        # === TOP ROW: NEW UI BADGE ===
        badge_row = QHBoxLayout()
        badge = BodyLabel("✨ MODERNIZED UI v2.0")
        badge.setStyleSheet(f"""
            background-color: #FFD700;
            color: #000000;
            padding: 6px 16px;
            border-radius: 16px;
            font-weight: {FONT_WEIGHT_BOLD};
            font-size: 12px;
        """)
        badge_row.addWidget(badge)
        badge_row.addStretch()
        layout.addLayout(badge_row)

        # === HERO ROW: Icon + Status ===
        hero_row = QHBoxLayout()
        hero_row.setSpacing(24)

        # HUGE icon
        self.status_icon_widget = IconWidget(ICON_MICROPHONE, card)
        self.status_icon_widget.setFixedSize(80, 80)  # 3x larger!

        # Text container
        text_container = QVBoxLayout()
        text_container.setSpacing(8)

        # HUGE status text
        self.status_text = StrongBodyLabel("Ready to Record")
        self.status_text.setStyleSheet(f"""
            font-size: 36px;
            font-weight: {FONT_WEIGHT_BOLD};
            color: #FFFFFF;
            letter-spacing: 1px;
        """)

        # Subtitle
        status_subtitle = CaptionLabel("Press Ctrl+Alt hotkey to start recording")
        status_subtitle.setStyleSheet(f"""
            font-size: 16px;
            color: #E0E0E0;
            font-weight: {FONT_WEIGHT_MEDIUM};
        """)

        text_container.addWidget(self.status_text)
        text_container.addWidget(status_subtitle)

        hero_row.addWidget(self.status_icon_widget)
        hero_row.addLayout(text_container)
        hero_row.addStretch()

        layout.addLayout(hero_row)

        # === DRAMATIC divider ===
        divider = QWidget()
        divider.setFixedHeight(2)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.3);")
        layout.addWidget(divider)

        # === FEATURE PILLS with colored backgrounds ===
        features_row = QHBoxLayout()
        features_row.setSpacing(16)

        # Hotkey pill - BLUE
        hotkey_pill = self._create_feature_pill(
            "⌨️ Ctrl+Alt",
            "Global hotkey",
            "#1890FF",
            FIF.EXPRESSIVE_INPUT_ENTRY
        )

        # Speed pill - GREEN
        speed_pill = self._create_feature_pill(
            "⚡ Instant",
            "Release to transcribe",
            "#52C41A",
            FIF.SPEED_OFF
        )

        # Privacy pill - AMBER
        privacy_pill = self._create_feature_pill(
            "🔒 100% Private",
            "All processing local",
            "#FAAD14",
            FIF.FOLDER
        )

        features_row.addWidget(hotkey_pill)
        features_row.addWidget(speed_pill)
        features_row.addWidget(privacy_pill)
        features_row.addStretch()

        layout.addLayout(features_row)

        return card

    def _create_feature_pill(self, title, subtitle, color, icon):
        """Create colorful feature pill"""
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 12px;
                padding: 12px 16px;
            }}
        """)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Icon
        icon_widget = IconWidget(icon)
        icon_widget.setFixedSize(24, 24)
        icon_widget.setStyleSheet("color: white;")
        layout.addWidget(icon_widget)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = StrongBodyLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: {FONT_WEIGHT_BOLD};
            color: #FFFFFF;
        """)

        subtitle_label = CaptionLabel(subtitle)
        subtitle_label.setStyleSheet(f"""
            font-size: 11px;
            color: rgba(255, 255, 255, 0.9);
        """)

        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        layout.addLayout(text_layout)

        return container

    def _create_feature_item(self, icon, title, subtitle):
        """Create a feature item with icon and text"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        # Icon
        icon_widget = IconWidget(icon, container)
        icon_widget.setFixedSize(20, 20)

        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)

        title_label = BodyLabel(title)
        title_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_SMALL}px;
            font-weight: {FONT_WEIGHT_SEMIBOLD};
            color: {COLOR_TEXT_PRIMARY};
        """)

        subtitle_label = CaptionLabel(subtitle)
        subtitle_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_CAPTION}px;
            color: {COLOR_TEXT_TERTIARY};
        """)

        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)

        layout.addWidget(icon_widget)
        layout.addLayout(text_layout)

        return container

    def update_status(self, recording: bool):
        """Update status widget and toggle Start/Stop button"""
        try:
            if hasattr(self, 'btn_record') and self.btn_record:
                # Disconnect existing connections to avoid duplicates
                try:
                    self.btn_record.clicked.disconnect()
                except Exception:
                    pass

                if recording:
                    self.btn_record.setText("Stop Recording")
                    # Use STOP icon if available; fallback to MICROPHONE
                    try:
                        self.btn_record.setIcon(FIF.STOP)
                    except Exception:
                        self.btn_record.setIcon(FIF.MICROPHONE)
                    self.btn_record.clicked.connect(self.stop_recording_clicked)
                else:
                    self.btn_record.setText("Start Recording")
                    self.btn_record.setIcon(FIF.MICROPHONE)
                    self.btn_record.clicked.connect(self.start_listening_clicked)
        except Exception:
            # UI safety: never crash on status updates
            pass

    def _create_test_transcription(self):
        """Modern test area with clean layout"""
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        layout.setSpacing(SPACING_MD)

        # Header row with icon and button
        header_row = QHBoxLayout()
        header_row.setSpacing(SPACING_SM)

        # Icon
        icon_widget = IconWidget(ICON_TEST, card)
        icon_widget.setFixedSize(24, 24)

        # Title and description
        text_container = QVBoxLayout()
        text_container.setSpacing(SPACING_XS)

        title = StrongBodyLabel("Test AI Formatting")
        title.setStyleSheet(f"""
            font-size: {FONT_SIZE_H2}px;
            font-weight: {FONT_WEIGHT_SEMIBOLD};
        """)

        desc = CaptionLabel("Preview how AI formats your speech (numbers, punctuation, capitalization)")
        desc.setStyleSheet(f"""
            font-size: {FONT_SIZE_CAPTION}px;
            color: {COLOR_TEXT_SECONDARY};
        """)

        text_container.addWidget(title)
        text_container.addWidget(desc)

        test_btn = PrimaryPushButton(ICON_PLAY, "Test")
        test_btn.clicked.connect(self._on_test_transcribe)
        test_btn.setFixedSize(100, 32)

        header_row.addWidget(icon_widget)
        header_row.addLayout(text_container)
        header_row.addStretch()
        header_row.addWidget(test_btn)

        # Input/Output row
        io_row = QHBoxLayout()
        io_row.setSpacing(SPACING_MD)

        # Input area
        input_container = QVBoxLayout()
        input_container.setSpacing(SPACING_XS)

        input_label = CaptionLabel("Input")
        input_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_CAPTION}px;
            color: {COLOR_TEXT_SECONDARY};
            font-weight: {FONT_WEIGHT_SEMIBOLD};
        """)

        self.test_input = TextEdit()
        self.test_input.setPlaceholderText("Type text to test formatting...")
        self.test_input.setFixedHeight(80)

        input_container.addWidget(input_label)
        input_container.addWidget(self.test_input)

        # Output area
        output_container = QVBoxLayout()
        output_container.setSpacing(SPACING_XS)

        output_label = CaptionLabel("Formatted Output")
        output_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_CAPTION}px;
            color: {COLOR_TEXT_SECONDARY};
            font-weight: {FONT_WEIGHT_SEMIBOLD};
        """)

        self.test_output = TextEdit()
        self.test_output.setPlaceholderText("AI formatted output will appear here...")
        self.test_output.setReadOnly(True)
        self.test_output.setFixedHeight(80)

        output_container.addWidget(output_label)
        output_container.addWidget(self.test_output)

        io_row.addLayout(input_container)
        io_row.addLayout(output_container)

        layout.addLayout(header_row)
        layout.addLayout(io_row)

        return card

    def _on_test_transcribe(self):
        """Handle test transcription button click"""
        test_text = self.test_input.toPlainText()
        if test_text.strip():
            # For now, just echo the text with confirmation
            # Later: add actual AI formatting logic
            self.test_output.setPlainText(f"Formatted: {test_text}")
        else:
            self.test_output.setPlainText("Please enter some text to test")

    def _create_metrics(self):
        """Create metrics cards with real data"""
        # Get real metrics from ValueCalculator
        if self.value_calculator:
            summary = self.value_calculator.get_session_summary()

            # Format time saved (convert seconds to hours and minutes)
            time_saved_seconds = summary.time_saved_vs_typing
            hours = int(time_saved_seconds // 3600)
            minutes = int((time_saved_seconds % 3600) // 60)
            time_saved_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

            # Format word count
            words_str = f"{summary.total_words:,}"

            # Format accuracy as percentage
            accuracy_str = f"{summary.accuracy_score * 100:.1f}%"

            # Format command count
            commands_str = f"{summary.total_commands}"
        else:
            # Fallback to sample data if no calculator
            time_saved_str = "0m"
            words_str = "0"
            accuracy_str = "0.0%"
            commands_str = "0"

        self.time_card = ValueCard(
            FIF.HISTORY,
            "Time Saved",
            time_saved_str,
            "This session",
            ""
        )

        self.words_card = ValueCard(
            FIF.PENCIL_INK,
            "Words Transcribed",
            words_str,
            "This session",
            ""
        )

        self.accuracy_card = ValueCard(
            FIF.CERTIFICATE,
            "Accuracy",
            accuracy_str,
            "Average confidence",
            ""
        )

        self.commands_card = ValueCard(
            FIF.COMMAND_PROMPT,
            "Commands",
            commands_str,
            "Voice commands",
            ""
        )

        # Create FlowLayout for metrics
        metrics_flow = FlowLayout()
        metrics_flow.setContentsMargins(0, 0, 0, 0)
        metrics_flow.setVerticalSpacing(SPACING_MD)
        metrics_flow.setHorizontalSpacing(SPACING_MD)

        # Add all cards to flow layout
        for card in [self.time_card, self.words_card, self.accuracy_card, self.commands_card]:
            card.setFixedSize(240, 120)  # Consistent card size
            metrics_flow.addWidget(card)

        # Wrap in container widget
        container = QWidget()
        container.setLayout(metrics_flow)

        return container

    def refresh_metrics(self):
        """Refresh metric cards with latest data"""
        if not self.value_calculator:
            return

        summary = self.value_calculator.get_session_summary()

        # Update time saved
        if self.time_card:
            time_saved_seconds = summary.time_saved_vs_typing
            hours = int(time_saved_seconds // 3600)
            minutes = int((time_saved_seconds % 3600) // 60)
            time_saved_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            self.time_card.set_value(time_saved_str)

        # Update word count
        if self.words_card:
            words_str = f"{summary.total_words:,}"
            self.words_card.set_value(words_str)

        # Update accuracy
        if self.accuracy_card:
            accuracy_str = f"{summary.accuracy_score * 100:.1f}%"
            self.accuracy_card.set_value(accuracy_str)

        # Update command count
        if self.commands_card:
            commands_str = f"{summary.total_commands}"
            self.commands_card.set_value(commands_str)
    
    def _create_stats_section(self):
        """Create stats section with simple header"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)
        
        # Simple section header
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        title = SubtitleLabel("Today's Activity")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addWidget(header_container)
        
        # Stats cards with staggered heights for visual interest
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.stat_transcriptions = StatCard(
            FIF.DOCUMENT,
            "Transcriptions",
            "0",
            parent=self
        )
        stats_layout.addWidget(self.stat_transcriptions)
        
        self.stat_words = StatCard(
            FIF.EDIT,
            "Words Saved",
            "0",
            "Total typed for you",
            parent=self
        )
        stats_layout.addWidget(self.stat_words)
        
        self.stat_time = StatCard(
            FIF.HISTORY,
            "Time Saved",
            "0m",
            "Estimated typing time",
            parent=self
        )
        stats_layout.addWidget(self.stat_time)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        return container
    
    def _create_welcome_section(self):
        """Create simple welcome section"""
        container = CardWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)
        
        # Simple welcome text
        title = SubtitleLabel("Ready to transcribe")
        layout.addWidget(title)
        
        subtitle = BodyLabel("Press Ctrl+Alt anywhere to start recording")
        subtitle.setTextColor(QColor(150, 150, 150), QColor(150, 150, 150))
        layout.addWidget(subtitle)
        
        return container
    
    def _create_quick_actions(self):
        """Create quick actions as cards for better visual hierarchy"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)
        
        # Start Recording Card
        self.record_card = QuickActionCard(
            FIF.MICROPHONE,
            "Start Recording",
            "Press to begin",
            parent=self
        )
        self.record_card.clicked.connect(self.start_listening_clicked)
        layout.addWidget(self.record_card)
        
        # View History Card
        self.history_card = QuickActionCard(
            FIF.HISTORY,
            "View History",
            "Browse past logs",
            parent=self
        )
        self.history_card.clicked.connect(self.view_history_clicked)
        layout.addWidget(self.history_card)
        
        # View Insights Card
        self.insights_card = QuickActionCard(
            FIF.INFO,
            "View Insights",
            "See productivity",
            parent=self
        )
        self.insights_card.clicked.connect(self.view_insights_clicked)
        layout.addWidget(self.insights_card)
        
        layout.addStretch()
        return container
    
    def _create_recent_activity(self):
        """Create recent activity section with simple header"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)
        
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        title = SubtitleLabel("Recent Activity")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addWidget(header_container)
        
        # Activity container
        self.activity_container = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setSpacing(SPACING_SM)
        self.activity_layout.setContentsMargins(0, 0, 0, 0)
        
        # Placeholder
        self.no_activity_label = BodyLabel("No recent transcriptions. Start recording to see activity!", self)
        self.activity_layout.addWidget(self.no_activity_label)
        
        layout.addWidget(self.activity_container)
        
        return container
    
    def update_stats(self, total_transcriptions: int, words_saved: int, time_saved_seconds: int):
        """Update statistics"""
        self.total_transcriptions = total_transcriptions
        self.words_saved = words_saved
        self.time_saved_seconds = time_saved_seconds
        
        # Update stat cards
        if hasattr(self, 'stat_transcriptions'):
            self.stat_transcriptions.update_value(str(total_transcriptions))
        if hasattr(self, 'stat_words'):
            self.stat_words.update_value(f"{words_saved:,}")
        if hasattr(self, 'stat_time'):
            minutes = time_saved_seconds // 60
            if minutes < 60:
                time_str = f"{minutes}m"
            else:
                hours = minutes // 60
                time_str = f"{hours}h {minutes % 60}m"
            self.stat_time.update_value(time_str)
    
    def update_recent_activity(self, transcriptions: list):
        """Update recent activity cards"""
        self.recent_transcriptions = transcriptions
        
        # Clear existing
        while self.activity_layout.count() > 0:
            item = self.activity_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not transcriptions:
            self.no_activity_label = BodyLabel("No recent transcriptions. Start recording to see activity!", self)
            self.activity_layout.addWidget(self.no_activity_label)
        else:
            # Show up to 5 recent transcriptions
            for trans in transcriptions[:5]:
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
