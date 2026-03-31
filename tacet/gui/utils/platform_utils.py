"""
Platform Detection Utilities

OS detection and platform-specific constants.
"""

import os
import sys
import platform


# Platform detection
IS_MAC = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

# Platform-specific key names
CTRL_KEY = "Command" if IS_MAC else "Control"
CTRL_SYMBOL = "⌘" if IS_MAC else "Ctrl"


def get_app_name():
    """Get the application name"""
    return "WhisperDictation"


def get_app_path():
    """Get the full path to the current script"""
    return os.path.abspath(sys.argv[0])
