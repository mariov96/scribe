"""
About Page - Version info, changelog, and resources
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    ScrollArea, TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel,
    CardWidget, TextEdit, HyperlinkButton, FluentIcon as FIF, isDarkTheme
)

from ..branding import SCRIBE_VERSION, CHANGELOG, get_contrasting_color, get_secondary_color
from ..widgets import BrandedHeader


class AboutPage(ScrollArea):
    """About page with version, changelog, and branding"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AboutPage")
        
        self.view = QWidget()
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        
        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(24)
        
        # Branding header
        header = BrandedHeader()
        
        # Version info card
        version_card = self._create_version_card()
        
        # Links card
        links_card = self._create_links_card()
        
        # Changelog
        changelog_label = SubtitleLabel("What's New")
        changelog_text = TextEdit()
        changelog_text.setMarkdown(CHANGELOG)
        changelog_text.setReadOnly(True)
        changelog_text.setMinimumHeight(400)
        
        self.vBoxLayout.addWidget(header)
        self.vBoxLayout.addWidget(version_card)
        self.vBoxLayout.addWidget(links_card)
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addWidget(changelog_label)
        self.vBoxLayout.addWidget(changelog_text)
        self.vBoxLayout.addStretch(1)
    
    def _create_version_card(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        version_label = SubtitleLabel(f"Version {SCRIBE_VERSION}")
        
        desc = BodyLabel(
            "The open voice platform. Community-driven successor to WhisperWriter, "
            "built for extensibility, privacy, and proving YOUR value through "
            "measurable productivity gains."
        )
        desc.setWordWrap(True)
        is_dark = isDarkTheme()
        desc.setTextColor(get_contrasting_color(is_dark), get_contrasting_color(is_dark))
        
        license_label = CaptionLabel("Licensed under Apache 2.0 • 100% Open Source")
        license_label.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        
        layout.addWidget(version_label)
        layout.addWidget(desc)
        layout.addWidget(license_label)
        
        return card
    
    def _create_links_card(self):
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        links_label = SubtitleLabel("Resources")
        
        github_link = HyperlinkButton(
            "https://github.com/yourusername/scribe",
            "GitHub Repository"
        )
        github_link.setIcon(FIF.GITHUB)
        
        docs_link = HyperlinkButton(
            "https://scribe-voice.dev",
            "Documentation"
        )
        docs_link.setIcon(FIF.BOOK_SHELF)
        
        discord_link = HyperlinkButton(
            "https://discord.gg/scribe",
            "Community Discord"
        )
        discord_link.setIcon(FIF.CHAT)
        
        layout.addWidget(links_label)
        layout.addWidget(github_link)
        layout.addWidget(docs_link)
        layout.addWidget(discord_link)
        
        return card
