"""
Icon Utilities

Functions for setting window icons.
"""

import os


def set_dialog_icon(dialog_window):
    """
    Set favicon icon for dialog window.

    Args:
        dialog_window: Tkinter window/dialog to set icon for
    """
    try:
        # Get path to favicon.ico
        here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        favicon_ico_path = os.path.join(here, "assets", "favicon.ico")

        if os.path.exists(favicon_ico_path):
            # Try multiple methods - one should work
            try:
                dialog_window.iconbitmap(default=favicon_ico_path)
            except Exception:
                try:
                    dialog_window.iconbitmap(bitmap=favicon_ico_path)
                except Exception:
                    dialog_window.wm_iconbitmap(favicon_ico_path)
    except Exception:
        pass  # Silently fail if icon can't be set


def get_icon_path(icon_name):
    """
    Get path to icon file in assets folder.

    Args:
        icon_name: Name of icon file (e.g., 'favicon.png')

    Returns:
        Full path to icon file
    """
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(here, "assets", icon_name)
