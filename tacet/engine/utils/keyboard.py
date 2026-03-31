"""
Keyboard Control Utilities

Functions for keyboard hotkey parsing and keyboard control.
"""

import re
from pynput import keyboard
from pynput.keyboard import Controller


# Hotkey mapping for user-friendly names to pynput format
KEY_MAP = {
    "ctrl": "<ctrl>", "control": "<ctrl>",
    "shift": "<shift>",
    "alt": "<alt>", "option": "<alt>",
    "win": "<cmd>", "windows": "<cmd>", "cmd": "<cmd>",
    "space": "<space>", "tab": "<tab>",
    "enter": "<enter>", "return": "<enter>",
    "esc": "<esc>", "escape": "<esc>",
}

# Modifier keys set
MODIFIER_KEYS = {
    keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
    keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
    keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
    keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
}


def normalize_hotkey(user_hotkey: str) -> str:
    """
    Normalize user hotkey string to pynput GlobalHotKeys format.

    Accepts formats like:
      - "ctrl+a"
      - "ctrl+;"
      - "ctrl+`"
      - "<ctrl>+a"

    Returns pynput format: "<ctrl>+a"

    Args:
        user_hotkey: User-friendly hotkey string

    Returns:
        Normalized hotkey string in pynput format

    Raises:
        ValueError: If hotkey token is unrecognized
    """
    hk = (user_hotkey or "").strip().lower()

    # Already in pynput format
    if "<" in hk and ">" in hk:
        return hk

    # Parse and normalize
    parts = [p.strip() for p in hk.split("+") if p.strip()]
    out = []

    for p in parts:
        # Function keys (f1, f2, etc.)
        if re.fullmatch(r"f\d{1,2}", p):
            out.append(f"<{p}>")
        # Known keys in KEY_MAP
        elif p in KEY_MAP:
            out.append(KEY_MAP[p])
        # Single character
        elif len(p) == 1:
            out.append(p)
        else:
            raise ValueError(f"Unrecognized hotkey token: '{p}'")

    return "+".join(out)


def backspace(kb: Controller, n: int):
    """
    Send backspace keystrokes via pynput Controller.

    Args:
        kb: pynput keyboard Controller instance
        n: Number of backspaces to send
    """
    n = max(0, int(n))
    for _ in range(n):
        kb.press(keyboard.Key.backspace)
        kb.release(keyboard.Key.backspace)
