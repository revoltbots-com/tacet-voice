"""
Icon Utilities

Functions for setting window icons.
"""

import os


def _get_project_root():
    """Get the project root directory (4 levels up from this file)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def set_dialog_icon(dialog_window):
    """
    Set favicon icon for dialog window.

    CustomTkinter overrides iconbitmap during window creation,
    so we defer the icon setting until after the window is mapped.

    Args:
        dialog_window: Tkinter window/dialog to set icon for
    """
    favicon_ico_path = os.path.join(_get_project_root(), "assets", "favicon.ico")
    if not os.path.exists(favicon_ico_path):
        return

    def _apply_icon():
        try:
            dialog_window.iconbitmap(favicon_ico_path)
        except Exception:
            pass

    # Defer so it runs after CustomTkinter finishes its own icon setup.
    # CTkToplevel sets its icon during the first draw cycle, so we need
    # to wait long enough for that to complete before overriding.
    try:
        dialog_window.after(200, _apply_icon)
    except Exception:
        pass

    # Bind Escape to close the dialog
    try:
        dialog_window.bind("<Escape>", lambda e: dialog_window.destroy())
    except Exception:
        pass


def get_icon_path(icon_name):
    """
    Get path to icon file in assets folder.

    Args:
        icon_name: Name of icon file (e.g., 'favicon.png')

    Returns:
        Full path to icon file
    """
    return os.path.join(_get_project_root(), "assets", icon_name)
