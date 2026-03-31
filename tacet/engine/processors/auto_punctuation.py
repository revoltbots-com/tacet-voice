"""
Auto-Punctuation Processor

Automatically adds punctuation based on speech patterns.
"""

import re


class AutoPunctuationProcessor:
    """
    Automatically adds punctuation based on speech patterns.

    Features:
    - Smart capitalization after sentence-ending punctuation
    - Capitalizes first letter of text
    - Configurable rules
    """

    def __init__(self, config: dict):
        """
        Initialize AutoPunctuationProcessor.

        Args:
            config: Dictionary containing:
                - enabled: Whether auto-punctuation is enabled
                - smart_capitals: Enable smart capitalization
                - period_on_pause: Add period on long pause (future)
                - comma_on_short_pause: Add comma on short pause (future)
        """
        self.enabled = config.get("enabled", False)
        self.smart_capitals = config.get("smart_capitals", True)
        self.period_on_pause = config.get("period_on_pause", False)
        self.comma_on_short_pause = config.get("comma_on_short_pause", False)

    def process_text(self, text: str) -> str:
        """
        Apply auto-punctuation rules to text.

        Args:
            text: Input text

        Returns:
            Text with punctuation added
        """
        if not self.enabled or not text:
            return text

        result = text

        # Smart capitalization: capitalize after sentence-ending punctuation
        if self.smart_capitals:
            # Capitalize letter after . ! ? followed by space
            result = re.sub(
                r'([.!?])\s+([a-z])',
                lambda m: m.group(1) + ' ' + m.group(2).upper(),
                result
            )
            # Also capitalize first letter of text if it's lowercase
            if result and result[0].islower():
                result = result[0].upper() + result[1:]

        return result
