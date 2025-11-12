"""
Scribe branding constants and colors
"""

SCRIBE_VERSION = "2.0.0-alpha"
SCRIBE_TAGLINE = "Voice Control for Your Workflow"
SCRIBE_PURPLE = "#6751A1"
SCRIBE_BLUE = "#4A90E2"

# UI Scaling - Reduced by 15% per user request
UI_SCALE_FACTOR = 0.85  # 15% smaller
DEFAULT_FONT_SIZE = 9  # Base font size in points (reduced from 11)

# Changelog
CHANGELOG = """
# Scribe Changelog

## v2.0.0-alpha (November 2025)
**Major Rewrite - The Open Voice Platform**

### 🎨 UI/UX Revolution
- Modern Fluent Design interface (PySide6)
- Scribe branding and visual identity
- Dark/Light theme with custom accent colors
- Analytics dashboard with insights
- Plugin management interface
- System tray integration

### 🔌 Plugin Architecture
- Extensible plugin system
- Window Manager plugin (14 voice commands)
- Plugin configuration UI
- Community plugin support

### 📊 Analytics & Value Tracking
- Time saved calculator
- Accuracy trends over time
- Command usage statistics
- Per-plugin metrics
- Insight generation from usage patterns

### 🔧 Modern Configuration
- YAML-based config system
- Pydantic validation
- Auto-generated settings UI
- Profile management

### 🚀 Performance
- faster-whisper integration
- Local-first processing (100% privacy)
- Optimized hotkey detection
- Background threading for responsiveness

---

## v1.x (WhisperWriter)
**Legacy Version - Unmaintained since January 2024**

### Features
- Basic voice transcription
- OpenAI Whisper integration
- Simple hotkey support
- Basic PyQt5 UI

---

**Scribe** is the community-driven successor to WhisperWriter,
built from the ground up to be extensible, privacy-first, and
focused on proving YOUR value through measurable productivity gains.
"""

# Contrasting colors for readability
# qfluentwidgets setTextColor takes (lightModeColor, darkModeColor)
def get_contrasting_colors():
    """Get text colors with good contrast for both themes.
    Returns: (light_mode_color, dark_mode_color)"""
    from PyQt5.QtGui import QColor
    # Light mode: very dark text, Dark mode: very light text
    return (QColor(20, 20, 20), QColor(240, 240, 240))


def get_secondary_colors():
    """Get secondary text colors with excellent contrast for both themes.
    Returns: (light_mode_color, dark_mode_color)"""
    from PyQt5.QtGui import QColor
    # Light mode: dark grey, Dark mode: light grey
    return (QColor(80, 80, 80), QColor(180, 180, 180))


# Legacy functions for backward compatibility
def get_contrasting_color(is_dark_theme: bool):
    """Get text color with good contrast"""
    from PyQt5.QtGui import QColor
    return QColor(240, 240, 240) if is_dark_theme else QColor(20, 20, 20)


def get_secondary_color(is_dark_theme: bool):
    """Get secondary text color with excellent contrast"""
    from PyQt5.QtGui import QColor
    return QColor(180, 180, 180) if is_dark_theme else QColor(80, 80, 80)
