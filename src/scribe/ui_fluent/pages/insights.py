"""
Insights Page - Analytics insights with AI-generated observations
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ScrollArea, TitleLabel, BodyLabel, isDarkTheme

from ..branding import get_secondary_color
from ..widgets import InsightCard


class InsightsPage(ScrollArea):
    """Analytics insights page with AI-generated observations"""
    
    def __init__(self, value_calculator=None, parent=None):
        super().__init__(parent)
        self.setObjectName("InsightsPage")
        
        self.value_calculator = value_calculator
        self.event_count = 0  # Track number of events received
        
        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        
        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(8)  # Tighter spacing (was 12)
        
        # Title
        self.title = TitleLabel("💡 Insights")
        self.subtitle = BodyLabel("AI-powered insights based on your usage patterns • More usage = Better insights")
        is_dark = isDarkTheme()
        self.subtitle.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        
        self.vBoxLayout.addWidget(self.title)
        self.vBoxLayout.addWidget(self.subtitle)
        self.vBoxLayout.addSpacing(4)  # Reduced from 8
        
        # Insights container - will be regenerated dynamically
        self.insights_layout = QVBoxLayout()
        self.insights_layout.setSpacing(8)  # Tighter spacing between cards
        self.vBoxLayout.addLayout(self.insights_layout)
        
        # Initial insights
        self._regenerate_insights()
        
        self.vBoxLayout.addStretch(1)
    
    def add_event(self, entry: dict):
        """Handle new transcription event for real-time insights"""
        self.event_count += 1
        
        # Regenerate insights every 2 new transcriptions
        if self.event_count % 2 == 0:
            self._regenerate_insights()
    
    def update_summary(self, summary):
        """Update insights with new summary data"""
        self._regenerate_insights()
    
    def _regenerate_insights(self):
        """Clear and regenerate all insight cards with current data"""
        # Clear existing insights
        while self.insights_layout.count():
            item = self.insights_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Generate fresh insights
        insights = self._generate_insights()
        
        # Add to layout
        for insight in insights:
            self.insights_layout.addWidget(insight)
    
    def _generate_insights(self):
        """Generate insights from real usage data"""
        insights = []
        
        if self.value_calculator:
            summary = self.value_calculator.get_session_summary()
            
            # Typing saved insight
            if summary.total_words > 0:
                time_saved_min = int(summary.time_saved_vs_typing / 60)
                insights.append(InsightCard(
                    "⚡",
                    "Typing Saved",
                    f"Based on average typing speed (40 wpm), you've saved the equivalent "
                    f"of typing {summary.total_words:,} words this session. That's {time_saved_min} minutes saved!",
                    f"{summary.total_words:,} words saved"
                ))
            
            # Productivity multiplier
            if summary.productivity_multiplier > 1.0:
                insights.append(InsightCard(
                    "🔥",
                    "Productivity Boost",
                    f"You're {summary.productivity_multiplier:.1f}x faster with Scribe than typing. "
                    f"That's a {int((summary.productivity_multiplier - 1) * 100)}% productivity gain!",
                    f"{summary.productivity_multiplier:.1f}x multiplier"
                ))
            
            # Accuracy insight
            if summary.accuracy_score > 0:
                insights.append(InsightCard(
                    "🎯",
                    "Transcription Quality",
                    f"Your transcription accuracy is {summary.accuracy_score * 100:.1f}%. "
                    f"Scribe is learning your voice patterns and vocabulary.",
                    f"{summary.accuracy_score * 100:.1f}% accuracy"
                ))
            
            # Command usage
            if summary.total_commands > 0:
                success_rate = (summary.successful_commands / summary.total_commands * 100) if summary.total_commands > 0 else 0
                insights.append(InsightCard(
                    "💡",
                    "Voice Commands",
                    f"You've used {summary.total_commands} voice commands with a {success_rate:.0f}% success rate. "
                    f"Voice commands save 3x more time than typing!",
                    f"{summary.total_commands} commands"
                ))
        
        # Add sample insights if no data yet
        if not insights:
            insights = [
                InsightCard(
                    "🎙️",
                    "Getting Started",
                    "Start using Scribe to see personalized insights about your productivity gains, "
                    "time saved, and transcription accuracy!",
                    "No data yet"
                ),
                InsightCard(
                    "⚡",
                    "Did You Know?",
                    "The average person types at 40 words per minute but speaks at 150 words per minute. "
                    "Scribe helps you work at the speed of thought!",
                    "3.75x faster"
                )
            ]
        
        return insights
