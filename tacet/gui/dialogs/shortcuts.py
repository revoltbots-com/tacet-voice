"""
Shortcuts Dialog

Configure keyboard shortcuts.
"""

import customtkinter as ctk
from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon
from tacet.gui.utils.shortcuts import normalize_shortcut, check_shortcut_conflicts

_translator = get_translator()


class ShortcutsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config = parent.engine.config.copy()

        self.title(_translator.t('shortcuts.dialog_title'))
        self.geometry("550x600")
        self.resizable(False, False)

        set_dialog_icon(self)
        self.transient(parent)
        self.grab_set()

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('shortcuts.title'),
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 15))

        # Scrollable frame for shortcuts
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=450)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Shortcuts configuration
        shortcuts = self.config.get('keyboard_shortcuts', {})
        self.shortcut_entries = {}

        for action, shortcut in shortcuts.items():
            self._create_shortcut_row(scroll_frame, action, shortcut)

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

    def _create_shortcut_row(self, parent, action, shortcut):
        """Create a row for a shortcut"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            frame,
            text=action,
            font=("Arial", 11),
            width=200,
            anchor="w"
        ).pack(side="left", padx=10)

        entry = ctk.CTkEntry(frame, width=150)
        entry.insert(0, shortcut)
        entry.pack(side="left", padx=5)

        self.shortcut_entries[action] = entry

    def _save(self):
        """Save shortcuts configuration"""
        shortcuts = {}
        for action, entry in self.shortcut_entries.items():
            shortcuts[action] = entry.get()

        self.config['keyboard_shortcuts'] = shortcuts
        self.parent.engine.update_config(self.config)
        self.destroy()
