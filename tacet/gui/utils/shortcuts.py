"""
Keyboard Shortcut Utilities

Functions for normalizing shortcuts and checking conflicts.
"""

from tacet.gui.utils.platform_utils import IS_MAC, IS_WINDOWS


def normalize_shortcut(shortcut_str):
    """
    Convert user-friendly shortcut (ctrl+s) to Tkinter format (<Control-s>).

    Args:
        shortcut_str: User-friendly shortcut string (e.g., 'ctrl+s')

    Returns:
        Tkinter-formatted shortcut string (e.g., '<Control-s>')
    """
    if not shortcut_str:
        return None

    # Handle special cases
    shortcut_lower = shortcut_str.lower().strip()

    # Map user notation to Tkinter notation
    parts = shortcut_lower.split('+')
    modifiers = []
    key = None

    for part in parts:
        part = part.strip()
        if part in ['ctrl', 'control']:
            modifiers.append('Command' if IS_MAC else 'Control')
        elif part in ['cmd', 'command']:
            modifiers.append('Command')
        elif part in ['shift']:
            modifiers.append('Shift')
        elif part in ['alt', 'option']:
            modifiers.append('Alt')
        elif part == 'comma':
            key = 'comma'
        elif part in ['escape', 'esc']:
            key = 'Escape'
        elif part.startswith('f') and len(part) == 2 and part[1].isdigit():
            # Function keys (f1, f2, etc.) need to be capitalized
            key = part.upper()
        else:
            key = part if len(part) > 1 else part.upper()

    if not key:
        return None

    # Build Tkinter format
    if modifiers:
        return f"<{'-'.join(modifiers)}-{key}>"
    else:
        return f"<{key}>"


def check_shortcut_conflicts(shortcut_str):
    """
    Check if shortcut conflicts with OS-level shortcuts.

    Args:
        shortcut_str: Shortcut string to check

    Returns:
        List of conflict warnings (empty if no conflicts)
    """
    conflicts = []
    shortcut_lower = shortcut_str.lower()

    if IS_WINDOWS:
        # Windows system shortcuts
        win_reserved = [
            'alt+f4', 'ctrl+alt+del', 'win+l', 'win+d',
            'alt+tab', 'ctrl+esc'
        ]
        if shortcut_lower in win_reserved:
            conflicts.append(f"{shortcut_str} is reserved by Windows")

    elif IS_MAC:
        # macOS system shortcuts
        mac_reserved = [
            'cmd+q', 'cmd+w', 'cmd+h', 'cmd+m', 'cmd+tab',
            'cmd+space', 'cmd+shift+3', 'cmd+shift+4'
        ]
        if shortcut_lower in mac_reserved or shortcut_lower.replace('ctrl', 'cmd') in mac_reserved:
            conflicts.append(f"{shortcut_str} is reserved by macOS")

    return conflicts
