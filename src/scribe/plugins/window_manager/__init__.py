"""
Window Manager Plugin - Control windows and applications by voice.

Day 1 plugin for Scribe that enables voice control of:
- Application switching ("switch to chrome")
- Window management ("minimize", "maximize", "close window")
- Desktop navigation
"""

from .plugin import WindowManager

__all__ = ["WindowManager"]
