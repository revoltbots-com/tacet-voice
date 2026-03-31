"""
Text Replacement Processor

Processes custom text replacements and abbreviations.
"""

import re


class TextReplacementProcessor:
    """
    Process custom text replacements/shortcuts.

    Allows users to define custom abbreviations and replacements.
    For example: "btw" -> "by the way"
    """

    def __init__(self, replacements_config: dict):
        """
        Initialize TextReplacementProcessor.

        Args:
            replacements_config: Dictionary containing:
                - enabled: Whether replacements are enabled
                - case_sensitive: Whether to match case
                - replacements: Dict of find -> replace mappings
        """
        self.enabled = replacements_config.get("enabled", False)
        self.case_sensitive = replacements_config.get("case_sensitive", False)
        self.replacements = replacements_config.get("replacements", {})

    def process_text(self, text: str) -> str:
        """
        Apply custom text replacements.

        Args:
            text: Input text

        Returns:
            Text with replacements applied
        """
        if not self.enabled or not text or not self.replacements:
            return text

        # Apply each replacement
        for find_text, replace_text in self.replacements.items():
            if self.case_sensitive:
                # Case-sensitive replacement
                text = text.replace(find_text, replace_text)
            else:
                # Case-insensitive replacement using regex
                pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                text = pattern.sub(replace_text, text)

        return text
