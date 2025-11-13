"""
Home Page - Dashboard with branding and metrics
"""

from PyQt5.QtCore import Qt, pyqtSignal as Signal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel,
    CardWidget, PrimaryPushButton, PushButton, FlowLayout,
    FluentIcon as FIF, isDarkTheme
)

from ..branding import get_secondary_color
from ..widgets import BrandedHeader, ValueCard


class HomePage(ScrollArea):
    """Home/Dashboard with branding"""

    # Signals for button actions
    start_listening_clicked = Signal()
    test_audio_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, value_calculator=None, parent=None):
        super().__init__(parent)
        self.setObjectName("HomePage")

        self.value_calculator = value_calculator
        
        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        
        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)  # Reduced significantly
        self.vBoxLayout.setSpacing(12)  # Reduced from 20
        
        # Branded header
        header = BrandedHeader()
        
        # Status card with background
        status_card = self._create_status_card()
        
        # Value metrics
        self.metrics_container = self._create_metrics()
        
        # Test transcription area (moved down, optional)
        test_card = self._create_test_transcription()
        
        self.vBoxLayout.addWidget(header)
        self.vBoxLayout.addWidget(status_card)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(self.metrics_container)
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addWidget(test_card)
        self.vBoxLayout.addStretch(1)
        
        # Store metric cards for updates
        self.time_card = None
        self.words_card = None
        self.accuracy_card = None
        self.commands_card = None
    
    def _create_status_card(self):
        """Create compact status card with prominent background"""
        from qfluentwidgets import StrongBodyLabel

        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(0)

        # Main status row with colored background
        self.status_container = QWidget()
        self.status_container.setStyleSheet("""
            QWidget {
                background-color: #2D5C2E;
                border-radius: 8px;
                padding: 12px 16px;
            }
        """)
        status_layout = QHBoxLayout(self.status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(12)

        self.status_icon = QLabel("🎤")
        self.status_icon.setStyleSheet("font-size: 28px; background: transparent;")

        self.status_text = TitleLabel("Ready to Record")
        self.status_text.setStyleSheet("font-size: 20px; font-weight: bold; color: #66FF66; background: transparent;")

        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()

        # Quick instructions in compact format
        instructions_widget = QWidget()
        instructions_layout = QHBoxLayout(instructions_widget)
        instructions_layout.setContentsMargins(0, 8, 0, 0)
        instructions_layout.setSpacing(16)

        # Quick key details - prominent and colorful
        details_widget = QWidget()
        details_layout = QHBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 8, 0, 0)
        details_layout.setSpacing(20)
        
        # Hotkey detail
        hotkey_label = BodyLabel('🎮 Hotkey: Ctrl+Alt')
        hotkey_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #AAAAFF;")
        
        # Release to transcribe
        release_label = BodyLabel('⚡ Release → Transcribe')
        release_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #AAFFAA;")
        
        # Privacy detail
        privacy_label = BodyLabel('� 100% Local & Private')
        privacy_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #FFAAAA;")

        details_layout.addWidget(hotkey_label)
        details_layout.addWidget(release_label)
        details_layout.addWidget(privacy_label)
        details_layout.addStretch()

        layout.addWidget(self.status_container)
        layout.addWidget(details_widget)

        return card
    
    def update_status(self, recording: bool):
        """Update status widget - disabled in favor of floating recording widget"""
        # Do nothing - the floating recording widget shows the recording status
        # Keep the home page status always in "Ready" state
        pass

    def _create_test_transcription(self):
        """Compact test area"""
        from qfluentwidgets import TextEdit

        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Header with test button inline
        header_row = QHBoxLayout()
        desc = BodyLabel("🧪 Test AI Formatting:")
        desc.setStyleSheet("font-weight: bold; font-size: 11px;")
        
        # Add description subtitle
        info_label = BodyLabel("Preview how AI formats your speech (numbers, punctuation, capitalization)")
        info_label.setStyleSheet("font-size: 9px; color: #888;")
        
        test_btn = PrimaryPushButton(FIF.PLAY, "Test")
        test_btn.clicked.connect(self._on_test_transcribe)
        test_btn.setFixedSize(80, 28)
        
        header_row.addWidget(desc)
        header_row.addWidget(info_label)
        header_row.addStretch()
        header_row.addWidget(test_btn)

        # Single row with input and output side by side
        io_row = QHBoxLayout()
        io_row.setSpacing(8)
        
        # Input area
        self.test_input = TextEdit()
        self.test_input.setPlaceholderText("Type text...")
        self.test_input.setFixedHeight(60)
        
        # Output area
        self.test_output = TextEdit()
        self.test_output.setPlaceholderText("Output...")
        self.test_output.setReadOnly(True)
        self.test_output.setFixedHeight(60)
        
        io_row.addWidget(self.test_input)
        io_row.addWidget(self.test_output)

        layout.addLayout(header_row)
        layout.addLayout(io_row)

        return card

    def _on_test_transcribe(self):
        """Handle test transcription button click"""
        test_text = self.test_input.toPlainText()
        if test_text.strip():
            # For now, just echo the text (later we can add AI formatting)
            self.test_output.setPlainText(f"✅ Transcribed: {test_text}")
        else:
            self.test_output.setPlainText("⚠️ Please enter some text to test")

    def _create_metrics(self):
        # Create FlowLayout directly without wrapper widget
        from qfluentwidgets import FlowLayout
        
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
            "Voice Commands",
            commands_str,
            "Times used",
            ""
        )
        
        # Create container with flow layout
        container = QWidget()
        layout = FlowLayout(container, needAni=False)  # Disable animation for better performance
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(self.time_card)
        layout.addWidget(self.words_card)
        layout.addWidget(self.accuracy_card)
        layout.addWidget(self.commands_card)
        
        return container
    
    def update_metrics(self):
        """Update metric cards with latest data from ValueCalculator"""
        if not self.value_calculator:
            return
            
        summary = self.value_calculator.get_session_summary()
        
        # Update time saved
        time_saved_seconds = summary.time_saved_vs_typing
        hours = int(time_saved_seconds // 3600)
        minutes = int((time_saved_seconds % 3600) // 60)
        time_saved_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        # Update words
        words_str = f"{summary.total_words:,}"
        
        # Update accuracy
        accuracy_str = f"{summary.accuracy_score * 100:.1f}%"
        
        # Update commands
        commands_str = f"{summary.total_commands}"
        
        # Update the card values
        if self.time_card:
            self.time_card.valueLabel.setText(time_saved_str)
        if self.words_card:
            self.words_card.valueLabel.setText(words_str)
        if self.accuracy_card:
            self.accuracy_card.valueLabel.setText(accuracy_str)
        if self.commands_card:
            self.commands_card.valueLabel.setText(commands_str)
