"""
Timestamp Processor

Handles timestamp insertion in transcriptions.
"""

import re
from datetime import datetime


class TimestampProcessor:
    """
    Handles timestamp insertion in transcriptions.

    Features:
    - Voice command trigger (say "insert timestamp")
    - Multiple formats: HH:MM:SS, HH:MM, 12-hour, date-time
    """

    def __init__(self, config: dict):
        """
        Initialize TimestampProcessor.

        Args:
            config: Dictionary containing:
                - enabled: Whether timestamps are enabled
                - format: Timestamp format (HH:MM:SS, HH:MM, 12-hour, date-time)
                - insert_mode: manual or auto
                - auto_on_paragraph: Auto-insert on paragraph breaks
                - voice_command: Command phrase to trigger insertion
        """
        self.enabled = config.get("enabled", False)
        self.format = config.get("format", "HH:MM:SS")
        self.insert_mode = config.get("insert_mode", "manual")
        self.auto_on_paragraph = config.get("auto_on_paragraph", False)
        self.voice_command = config.get("voice_command", "insert timestamp")

    def get_timestamp(self) -> str:
        """
        Get formatted timestamp string.

        Returns:
            Formatted timestamp based on configuration
        """
        now = datetime.now()

        format_map = {
            "HH:MM:SS": "%H:%M:%S",
            "HH:MM": "%H:%M",
            "12-hour": "%I:%M:%S %p",
            "date-time": "%Y-%m-%d %H:%M:%S",
        }

        fmt = format_map.get(self.format, "%H:%M:%S")
        return now.strftime(fmt)

    def process_text(self, text: str) -> str:
        """
        Process text for timestamp insertion.

        Args:
            text: Input text

        Returns:
            Text with timestamps if applicable
        """
        if not self.enabled or not text:
            return text

        result = text

        # Check for voice command trigger (case-insensitive)
        if self.voice_command:
            # Match the voice command as whole words
            pattern = r'\b' + re.escape(self.voice_command) + r'\b'
            if re.search(pattern, result, re.IGNORECASE):
                timestamp = self.get_timestamp()
                result = re.sub(pattern, timestamp, result, flags=re.IGNORECASE)

        return result
