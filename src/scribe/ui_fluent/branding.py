"""
Scribe Design System
Modern, consistent design constants for the entire application.
"""

from scribe.__version__ import __version__
from PyQt5.QtGui import QColor

SCRIBE_VERSION = __version__  # Now imports from __version__.py
SCRIBE_TAGLINE = "Voice Control for Your Workflow"

# ============================================================================
# COLOR PALETTE - Modern, accessible colors
# ============================================================================

# Brand Colors
SCRIBE_PURPLE = "#6751A1"  # Primary brand color
SCRIBE_BLUE = "#4A90E2"    # Secondary accent

# Semantic Colors (Dark Theme optimized)
COLOR_SUCCESS = "#52C41A"      # Green - success states
COLOR_WARNING = "#FAAD14"      # Amber - warning states
COLOR_ERROR = "#F5222D"        # Red - error states
COLOR_INFO = "#1890FF"         # Blue - informational states

# Recording States
COLOR_RECORDING = "#FF4D4F"    # Bright red for recording
COLOR_READY = "#52C41A"        # Green for ready state
COLOR_PROCESSING = "#FAAD14"   # Amber for processing

# Neutral Grays (Dark Theme)
COLOR_BG_PRIMARY = "#1E1E1E"       # Main background
COLOR_BG_SECONDARY = "#252525"     # Card backgrounds
COLOR_BG_TERTIARY = "#2D2D2D"      # Elevated surfaces
COLOR_BORDER = "#3A3A3A"           # Subtle borders
COLOR_DIVIDER = "#303030"          # Dividers

# Text Colors (Dark Theme)
COLOR_TEXT_PRIMARY = "#E8E8E8"     # Primary text
COLOR_TEXT_SECONDARY = "#A8A8A8"   # Secondary text
COLOR_TEXT_TERTIARY = "#707070"    # Tertiary text/hints
COLOR_TEXT_DISABLED = "#4A4A4A"    # Disabled text

# Text Colors (Light Theme)
COLOR_TEXT_PRIMARY_LIGHT = "#202020"     # Primary text
COLOR_TEXT_SECONDARY_LIGHT = "#606060"   # Secondary text
COLOR_TEXT_TERTIARY_LIGHT = "#909090"    # Tertiary text/hints

# ============================================================================
# TYPOGRAPHY SCALE - Clear hierarchy
# ============================================================================

# Font Sizes (in points)
FONT_SIZE_HERO = 24        # Hero text (main status)
FONT_SIZE_H1 = 20          # Page titles
FONT_SIZE_H2 = 16          # Section headers
FONT_SIZE_H3 = 14          # Subsection headers
FONT_SIZE_BODY = 13        # Body text (default)
FONT_SIZE_SMALL = 11       # Small text
FONT_SIZE_CAPTION = 10     # Captions, hints

# Font Weights
FONT_WEIGHT_LIGHT = "300"
FONT_WEIGHT_NORMAL = "400"
FONT_WEIGHT_MEDIUM = "500"
FONT_WEIGHT_SEMIBOLD = "600"
FONT_WEIGHT_BOLD = "700"

# ============================================================================
# SPACING SCALE - Consistent rhythm
# ============================================================================

SPACING_XS = 4      # Extra small - tight spacing
SPACING_SM = 8      # Small - compact elements
SPACING_MD = 16     # Medium - default spacing
SPACING_LG = 24     # Large - section spacing
SPACING_XL = 32     # Extra large - major sections
SPACING_XXL = 48    # Double extra large - page sections

# Component-specific spacing
CARD_PADDING = SPACING_MD
CARD_SPACING = SPACING_MD
SECTION_SPACING = SPACING_LG
PAGE_MARGIN = SPACING_LG

# ============================================================================
# BORDER RADIUS - Modern, consistent corners
# ============================================================================

RADIUS_SM = 4       # Small elements
RADIUS_MD = 8       # Cards, buttons
RADIUS_LG = 12      # Large cards
RADIUS_XL = 16      # Modal dialogs
RADIUS_ROUND = 999  # Fully rounded (pills)

# ============================================================================
# SHADOWS - Subtle depth
# ============================================================================

SHADOW_SM = "0 1px 2px rgba(0, 0, 0, 0.25)"
SHADOW_MD = "0 2px 8px rgba(0, 0, 0, 0.35)"
SHADOW_LG = "0 4px 16px rgba(0, 0, 0, 0.45)"

# ============================================================================
# ICON MAPPINGS - FluentIcons to replace emoji
# ============================================================================

from qfluentwidgets import FluentIcon as FIF

# Recording & Audio
ICON_MICROPHONE = FIF.MICROPHONE
ICON_RECORDING = FIF.MICROPHONE
ICON_VOLUME = FIF.VOLUME
ICON_SPEAKER = FIF.SPEAKERS

# UI Actions
ICON_PLAY = FIF.PLAY
ICON_PAUSE = FIF.PAUSE
ICON_STOP = FIF.STOP_WATCH
ICON_SETTINGS = FIF.SETTING
ICON_TEST = FIF.EXPRESSIVE_INPUT_ENTRY

# Status & Feedback
ICON_SUCCESS = FIF.COMPLETED
ICON_ERROR = FIF.CANCEL
ICON_WARNING = FIF.INFO
ICON_INFO = FIF.INFO

# Features
ICON_HOTKEY = FIF.EXPRESSIVE_INPUT_ENTRY  # Closest to keyboard
ICON_SPEED = FIF.SPEED_OFF
ICON_PRIVACY = FIF.FOLDER  # Using FOLDER as closest to lock
ICON_LOCAL = FIF.FOLDER
ICON_HISTORY = FIF.HISTORY
ICON_PLUGINS = FIF.APPLICATION
ICON_INSIGHTS = FIF.HISTORY  # Using HISTORY as closest to chart

# Navigation
ICON_HOME = FIF.HOME
ICON_BACK = FIF.CANCEL  # Using CANCEL as closest to back
ICON_FORWARD = FIF.PLAY  # Using PLAY as closest to forward arrow
ICON_UP = FIF.UP if hasattr(FIF, 'UP') else FIF.CARE_UP_SOLID
ICON_DOWN = FIF.DOWN if hasattr(FIF, 'DOWN') else FIF.CARE_DOWN_SOLID

# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================

UI_SCALE_FACTOR = 0.85  # 15% smaller (legacy)
DEFAULT_FONT_SIZE = FONT_SIZE_BODY  # Base font size

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
    return (QColor(32, 32, 32), QColor(240, 240, 240))


def get_secondary_colors():
    """Get secondary text colors with excellent contrast for both themes.
    Returns: (light_mode_color, dark_mode_color)"""
    from PyQt5.QtGui import QColor
    # Light mode: dark grey, Dark mode: light grey
    return (QColor(96, 96, 96), QColor(180, 180, 180))


# Legacy functions for backward compatibility
def get_contrasting_color(is_dark_theme: bool):
    """Get text color with good contrast"""
    from PyQt5.QtGui import QColor
    return QColor(240, 240, 240) if is_dark_theme else QColor(20, 20, 20)


def get_secondary_color(is_dark_theme: bool):
    """Get secondary text color with excellent contrast"""
    from PyQt5.QtGui import QColor
    return QColor(180, 180, 180) if is_dark_theme else QColor(80, 80, 80)
