"""
Scribe Branded Header Widget
Displays logo, title, and tagline
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from qfluentwidgets import TitleLabel, BodyLabel, isDarkTheme

from ..branding import SCRIBE_TAGLINE, get_secondary_color


class BrandedHeader(QWidget):
    """Scribe branded header with logo and tagline"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        
        # Logo - Use microphone image instead of emoji
        from pathlib import Path
        from PyQt5.QtGui import QPixmap
        
        logo_label = QLabel()
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent.parent
        assets_dir = project_root / 'assets'
        
        # Try to load microphone.png
        mic_icon_path = assets_dir / 'microphone.png'
        if mic_icon_path.exists():
            pixmap = QPixmap(str(mic_icon_path))
            # Scale to 48x48
            pixmap = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            # Invert colors for dark mode
            if isDarkTheme():
                from PyQt5.QtGui import QImage, qRgb
                image = pixmap.toImage()
                image.invertPixels()
                pixmap = QPixmap.fromImage(image)

            logo_label.setPixmap(pixmap)
        else:
            # Fallback to emoji
            logo_label.setText("🎤")
            logo_label.setStyleSheet("font-size: 48px;")
        
        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        # Title
        title = TitleLabel("Scribe")
        title_font = title.font()
        title_font.setBold(True)
        title.setFont(title_font)
        
        # Tagline
        tagline = BodyLabel(SCRIBE_TAGLINE)
        is_dark = isDarkTheme()
        tagline.setTextColor(get_secondary_color(is_dark), get_secondary_color(is_dark))
        
        text_layout.addWidget(title)
        text_layout.addWidget(tagline)
        
        layout.addWidget(logo_label)
        layout.addLayout(text_layout)
        layout.addStretch()
