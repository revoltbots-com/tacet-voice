"""
Translation Manager

Manages UI translations from languages.json for multi-language support.
"""

import json
import os


class TranslationManager:
    """
    Manages UI translations from languages.json.

    Provides translation lookup for multi-language UI support.
    """

    def __init__(self):
        """Initialize TranslationManager and load translations."""
        self.translations = {}
        self.current_lang = "en"
        self._load_translations()

    def _load_translations(self):
        """Load translations from languages.json"""
        try:
            # Find languages.json in root directory
            here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            lang_file = os.path.join(here, "languages.json")

            if os.path.exists(lang_file):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Remove _info section
                    self.translations = {k: v for k, v in data.items() if not k.startswith('_')}
            else:
                # Fallback to English if file doesn't exist
                self.translations = {"en": self._get_default_english()}
        except Exception as e:
            print(f"Warning: Could not load translations: {e}")
            self.translations = {"en": self._get_default_english()}

    def _get_default_english(self):
        """Minimal English fallback if languages.json is missing"""
        return {
            "name": "English",
            "buttons": {
                "save": "💾 Save",
                "export": "📤 Export",
                "settings": "⚙ Settings",
                "stats": "📊 Stats",
                "about": "ℹ About",
                "copy": "📋 Copy",
                "clear": "Clear"
            }
        }

    def set_language(self, lang_code):
        """
        Set current UI language.

        Args:
            lang_code: Language code (e.g., 'en', 'es', 'fr')

        Returns:
            True if language was set successfully, False otherwise
        """
        if lang_code in self.translations:
            self.current_lang = lang_code
            return True
        return False

    def get_available_languages(self):
        """
        Get list of available languages.

        Returns:
            Dict mapping language codes to language names
        """
        return {code: data.get("name", code) for code, data in self.translations.items()}

    def t(self, key_path, **kwargs):
        """
        Get translated string by key path (e.g., 'buttons.save').

        Supports variable substitution: t('stats.words_per_min', wpm=120)

        Args:
            key_path: Dot-separated key path (e.g., 'buttons.save')
            **kwargs: Variables for string formatting

        Returns:
            Translated string, or key path if translation not found
        """
        keys = key_path.split('.')
        value = self.translations.get(self.current_lang, {})

        # Navigate through nested dict
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break

        # Fallback to English if not found
        if value is None:
            value = self.translations.get('en', {})
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    value = None
                    break

        # If still not found, return the key path
        if value is None:
            return key_path

        # Handle variable substitution
        if kwargs and isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError:
                return value

        return value


# Global translation manager singleton
_translator = None


def get_translator():
    """
    Get or create the global translation manager.

    Returns:
        TranslationManager instance
    """
    global _translator
    if _translator is None:
        _translator = TranslationManager()
    return _translator
