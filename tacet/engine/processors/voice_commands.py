"""
Voice Command Processor

Processes voice commands in transcribed text and executes keyboard actions.
"""

import platform
import time
from pynput import keyboard
from pynput.keyboard import Controller


class VoiceCommandProcessor:
    """
    Process voice commands in transcribed text.

    Detects command phrases (e.g., "period", "new line", "delete") in
    transcribed text and executes corresponding keyboard actions.
    """

    def __init__(self, commands_config: dict):
        """
        Initialize VoiceCommandProcessor.

        Args:
            commands_config: Dictionary containing:
                - enabled: Whether commands are enabled
                - commands: Dict of command phrases and their configurations
        """
        self.enabled = commands_config.get("enabled", True)
        self.commands = commands_config.get("commands", {})
        self.kb = Controller()

    def process_text(self, text: str) -> str:
        """
        Process text for voice commands and execute them.

        Args:
            text: Transcribed text potentially containing commands

        Returns:
            Text with commands removed
        """
        if not self.enabled or not text:
            return text

        # Normalize text (lowercase for matching)
        text_lower = text.lower().strip()

        # Check each command
        for command_phrase, command_config in self.commands.items():
            if not command_config.get("enabled", True):
                continue

            # Check if command is at the end of text (most common case)
            if text_lower.endswith(command_phrase):
                # Execute the command
                self._execute_command(command_config)

                # Remove command from text (preserving original case)
                start_idx = len(text) - len(command_phrase)
                text = text[:start_idx].rstrip()
                text_lower = text.lower()

        return text

    def _execute_command(self, command_config: dict):
        """Execute a single voice command"""
        command_type = command_config.get("type")

        if command_type == "type_char":
            # Type a character (e.g., period, comma)
            char = command_config.get("char", "")
            if char:
                self.kb.type(char)

        elif command_type == "press_key":
            # Press a key (e.g., enter, tab)
            key_name = command_config.get("key", "")
            if key_name:
                self._press_key(key_name)

        elif command_type == "delete_word":
            # Delete previous word
            self._delete_words(1)

        elif command_type == "delete_line":
            # Delete current line
            self._delete_line()

        elif command_type == "caps_on":
            # Enable caps lock
            self.kb.press(keyboard.Key.caps_lock)
            self.kb.release(keyboard.Key.caps_lock)

        elif command_type == "caps_off":
            # Disable caps lock
            self.kb.press(keyboard.Key.caps_lock)
            self.kb.release(keyboard.Key.caps_lock)

    def _press_key(self, key_name: str):
        """Press a special key"""
        key_map = {
            "enter": keyboard.Key.enter,
            "tab": keyboard.Key.tab,
            "space": keyboard.Key.space,
            "backspace": keyboard.Key.backspace,
            "delete": keyboard.Key.delete,
            "up": keyboard.Key.up,
            "down": keyboard.Key.down,
            "left": keyboard.Key.left,
            "right": keyboard.Key.right,
        }

        key = key_map.get(key_name.lower())
        if key:
            self.kb.press(key)
            self.kb.release(key)

    def _delete_words(self, count: int):
        """Delete specified number of words backwards"""
        for _ in range(count):
            # Ctrl+Backspace deletes word on Windows/Linux
            # Option+Backspace on macOS
            if platform.system() == "Darwin":
                self.kb.press(keyboard.Key.alt)
            else:
                self.kb.press(keyboard.Key.ctrl)

            self.kb.press(keyboard.Key.backspace)
            self.kb.release(keyboard.Key.backspace)

            if platform.system() == "Darwin":
                self.kb.release(keyboard.Key.alt)
            else:
                self.kb.release(keyboard.Key.ctrl)

            time.sleep(0.05)

    def _delete_line(self):
        """Delete current line"""
        # Select line then delete
        if platform.system() == "Darwin":
            # macOS: Cmd+Left, Shift+Cmd+Right, Delete
            self.kb.press(keyboard.Key.cmd)
            self.kb.press(keyboard.Key.left)
            self.kb.release(keyboard.Key.left)
            self.kb.release(keyboard.Key.cmd)

            self.kb.press(keyboard.Key.shift)
            self.kb.press(keyboard.Key.cmd)
            self.kb.press(keyboard.Key.right)
            self.kb.release(keyboard.Key.right)
            self.kb.release(keyboard.Key.cmd)
            self.kb.release(keyboard.Key.shift)
        else:
            # Windows/Linux: Home, Shift+End
            self.kb.press(keyboard.Key.home)
            self.kb.release(keyboard.Key.home)

            self.kb.press(keyboard.Key.shift)
            self.kb.press(keyboard.Key.end)
            self.kb.release(keyboard.Key.end)
            self.kb.release(keyboard.Key.shift)

        # Delete selection
        self.kb.press(keyboard.Key.delete)
        self.kb.release(keyboard.Key.delete)
