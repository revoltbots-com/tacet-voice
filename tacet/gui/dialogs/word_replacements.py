"""
Word Replacements Dialog

Configure custom word replacements and abbreviations.
Multi-language support with tabs for each language.
"""

import customtkinter as ctk
from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon
from tacet.gui.dialogs.components import EditorList, ItemRow

_translator = get_translator()

# Supported languages
LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch'
}


class WordReplacementsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config = parent.engine.config.copy()

        self.title(_translator.t('word_replacements.dialog_title'))
        self.geometry("750x600")
        self.resizable(False, False)

        set_dialog_icon(self)
        self.transient(parent)
        self.grab_set()

        # Storage for editor lists (one per language)
        self.editor_lists = {}

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('word_replacements.title'),
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 15))

        # Global enable checkbox
        self.enabled_var = ctk.BooleanVar(
            value=self.config.get('word_replacements', {}).get('enabled', True)
        )
        ctk.CTkCheckBox(
            main_frame,
            text=_translator.t('word_replacements.enable') if _translator.t('word_replacements.enable') != 'word_replacements.enable' else "Enable word replacements",
            variable=self.enabled_var,
            font=("Arial", 12)
        ).pack(pady=(0, 15), anchor="w")

        # Language tabs
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, pady=(0, 15))

        # Create tab for each language
        for lang_code, lang_name in LANGUAGES.items():
            self._create_language_tab(lang_code, lang_name)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        ctk.CTkButton(
            button_frame,
            text=_translator.t('buttons.save'),
            command=self._save,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text=_translator.t('buttons.cancel'),
            command=self.destroy,
            width=100,
            fg_color="gray"
        ).pack(side="left", padx=5)

    def _create_language_tab(self, lang_code, lang_name):
        """Create editor tab for a language"""
        # Add tab
        tab = self.tabview.add(lang_name)

        # Language enable checkbox
        lang_config = self.config.get('word_replacements', {}).get('dictionaries', {}).get(lang_code, {})
        lang_enabled_var = ctk.BooleanVar(value=lang_config.get('enabled', False))

        checkbox_frame = ctk.CTkFrame(tab, fg_color="transparent")
        checkbox_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkCheckBox(
            checkbox_frame,
            text=f"Enable {lang_name} replacements",
            variable=lang_enabled_var,
            font=("Arial", 11)
        ).pack(anchor="w")

        # Store enabled var
        if not hasattr(self, 'lang_enabled_vars'):
            self.lang_enabled_vars = {}
        self.lang_enabled_vars[lang_code] = lang_enabled_var

        # Create EditorList for this language
        editor = EditorList(
            tab,
            item_factory=lambda data: self._create_replacement_row(data, lang_code),
            on_add=lambda lc=lang_code: self._add_replacement(lc),
            on_delete=None,  # Handled by ItemRow delete button
            on_reset=lambda lc=lang_code: self._reset_replacements(lc),
            buttons_config={'add': True, 'delete': False, 'reset': True}
        )
        editor.pack(fill="both", expand=True)

        # Store editor reference
        self.editor_lists[lang_code] = editor

        # Load replacements for this language
        self._load_replacements(lang_code)

    def _load_replacements(self, lang_code):
        """Load replacements for a language into editor"""
        lang_config = self.config.get('word_replacements', {}).get('dictionaries', {}).get(lang_code, {})
        replacements = lang_config.get('replacements', {})

        for find_text, replace_text in replacements.items():
            item_data = {
                'id': find_text,
                'find': find_text,
                'replace': replace_text
            }
            self.editor_lists[lang_code].add_item(item_data)

    def _create_replacement_row(self, item_data, lang_code):
        """
        Factory method to create ItemRow for a word replacement.

        Args:
            item_data: Dict with keys: id, find, replace
            lang_code: Language code for this row

        Returns:
            ItemRow widget instance
        """
        # Configure row layout
        row_config = {
            'fields': [
                {'name': 'find', 'label': 'Find', 'width': 200, 'readonly': False},
                {'name': 'replace', 'label': 'Replace', 'width': 250, 'readonly': False}
            ],
            'show_enabled': False,
            'show_delete': True,
            'show_edit': False
        }

        # Create and return ItemRow
        return ItemRow(
            self.editor_lists[lang_code].scroll_frame,
            item_id=item_data['id'],
            item_data=item_data,
            config=row_config,
            on_change=lambda item_id, data: self._on_replacement_changed(lang_code, item_id, data),
            on_delete=lambda item_id: self._delete_replacement(lang_code, item_id),
            on_edit=None
        )

    def _on_replacement_changed(self, lang_code, item_id, data):
        """Handle replacement data change"""
        # Data is automatically tracked, will be collected on save
        pass

    def _add_replacement(self, lang_code):
        """Add new empty replacement to language"""
        # Generate unique ID
        import time
        item_id = f"new_{int(time.time() * 1000)}"

        item_data = {
            'id': item_id,
            'find': '',
            'replace': ''
        }
        self.editor_lists[lang_code].add_item(item_data)

    def _delete_replacement(self, lang_code, item_id):
        """Delete replacement from language"""
        self.editor_lists[lang_code].remove_item(item_id)

    def _reset_replacements(self, lang_code):
        """Reset replacements for language to defaults"""
        # Get default config
        default_config = self.parent.engine.get_default_config()
        default_replacements = default_config.get('word_replacements', {}).get('dictionaries', {}).get(lang_code, {}).get('replacements', {})

        # Update current config
        if 'word_replacements' not in self.config:
            self.config['word_replacements'] = {}
        if 'dictionaries' not in self.config['word_replacements']:
            self.config['word_replacements']['dictionaries'] = {}
        if lang_code not in self.config['word_replacements']['dictionaries']:
            self.config['word_replacements']['dictionaries'][lang_code] = {}

        self.config['word_replacements']['dictionaries'][lang_code]['replacements'] = default_replacements.copy()

        # Refresh editor
        self.editor_lists[lang_code].clear_items()
        self._load_replacements(lang_code)

    def _save(self):
        """Save word replacements configuration"""
        # Update global enabled flag
        self.config['word_replacements']['enabled'] = self.enabled_var.get()

        # Update each language
        for lang_code, editor in self.editor_lists.items():
            # Get all replacements for this language
            items_data = editor.get_all_items()

            # Build replacements dict
            replacements = {}
            for item_data in items_data:
                find_text = item_data.get('find', '').strip()
                replace_text = item_data.get('replace', '').strip()

                # Only save non-empty replacements
                if find_text and replace_text:
                    replacements[find_text] = replace_text

            # Update config
            if lang_code not in self.config['word_replacements']['dictionaries']:
                self.config['word_replacements']['dictionaries'][lang_code] = {}

            self.config['word_replacements']['dictionaries'][lang_code]['replacements'] = replacements
            self.config['word_replacements']['dictionaries'][lang_code]['enabled'] = self.lang_enabled_vars[lang_code].get()

        # Save to engine
        self.parent.engine.update_config(self.config)
        self.destroy()
