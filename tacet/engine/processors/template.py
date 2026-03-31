"""
Template Processor

Expands template triggers into full text snippets.
"""

import re


class TemplateProcessor:
    """
    Expands template triggers into full text snippets.

    Features:
    - Say trigger phrase → expands to pre-defined text
    - Case-insensitive matching
    - Manage snippets via configuration
    """

    def __init__(self, config: dict):
        """
        Initialize TemplateProcessor.

        Args:
            config: Dictionary containing:
                - enabled: Whether templates are enabled
                - snippets: Dict of snippet configurations
        """
        self.enabled = config.get("enabled", False)
        self.snippets = config.get("snippets", {})

    def process_text(self, text: str) -> str:
        """
        Apply template expansion to text.

        Args:
            text: Input text

        Returns:
            Text with templates expanded
        """
        if not self.enabled or not text or not self.snippets:
            return text

        result = text

        # Check for template triggers
        for snippet_id, snippet_config in self.snippets.items():
            if not snippet_config.get("enabled", True):
                continue

            trigger = snippet_config.get("trigger", "")
            template_text = snippet_config.get("text", "")

            if trigger and template_text:
                # Match trigger as whole word (case-insensitive)
                pattern = r'\b' + re.escape(trigger) + r'\b'
                if re.search(pattern, result, re.IGNORECASE):
                    # Replace trigger with template text
                    result = re.sub(pattern, template_text, result, flags=re.IGNORECASE)

        return result

    def get_snippets(self) -> dict:
        """
        Get all available snippets.

        Returns:
            Dictionary of snippet configurations
        """
        return self.snippets
