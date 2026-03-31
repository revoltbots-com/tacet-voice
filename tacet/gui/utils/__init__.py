"""
GUI Utilities

Platform detection, keyboard shortcuts, auto-start, and icon helpers.
"""

from tacet.gui.utils.platform_utils import (
    IS_MAC,
    IS_WINDOWS,
    IS_LINUX,
    CTRL_KEY,
    CTRL_SYMBOL,
    get_app_name,
    get_app_path,
)
from tacet.gui.utils.shortcuts import normalize_shortcut, check_shortcut_conflicts
from tacet.gui.utils.autostart import enable_auto_start, disable_auto_start
from tacet.gui.utils.icons import set_dialog_icon, get_icon_path

__all__ = [
    # Platform
    "IS_MAC",
    "IS_WINDOWS",
    "IS_LINUX",
    "CTRL_KEY",
    "CTRL_SYMBOL",
    "get_app_name",
    "get_app_path",
    # Shortcuts
    "normalize_shortcut",
    "check_shortcut_conflicts",
    # Auto-start
    "enable_auto_start",
    "disable_auto_start",
    # Icons
    "set_dialog_icon",
    "get_icon_path",
]
