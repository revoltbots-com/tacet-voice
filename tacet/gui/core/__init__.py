"""
GUI Core Components

Translation manager and system tray integration.
"""

from tacet.gui.core.translation import TranslationManager, get_translator
from tacet.gui.core.system_tray import TrayIcon

__all__ = ["TranslationManager", "get_translator", "TrayIcon"]
