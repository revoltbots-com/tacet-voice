"""
Settings Dialog

Main configuration dialog for all application settings.
"""

import os
import customtkinter as ctk
from tkinter import messagebox

from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon
from tacet.engine.utils.audio import list_input_devices
from tacet.gui.dialogs.voice_commands import VoiceCommandsDialog
from tacet.gui.dialogs.word_replacements import WordReplacementsDialog
from tacet.gui.dialogs.templates import TemplatesDialog

_translator = get_translator()


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.parent = parent
        self.engine = engine
        self.config = engine.config.copy()

        self.title(_translator.t('settings.dialog_title'))
        self.geometry("550x750")
        self.resizable(False, False)

        set_dialog_icon(self)
        self.transient(parent)
        self.grab_set()

        # Create tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Add tabs
        self.tabview.add(_translator.t('settings.tab_engine'))
        self.tabview.add(_translator.t('settings.tab_audio'))
        self.tabview.add(_translator.t('settings.tab_behavior'))
        self.tabview.add(_translator.t('settings.tab_hotkey'))

        # Setup each tab
        self._setup_engine_tab()
        self._setup_audio_tab()
        self._setup_behavior_tab()
        self._setup_hotkey_tab()

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

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

    def _setup_engine_tab(self):
        """Setup engine configuration tab"""
        tab = self.tabview.tab(_translator.t('settings.tab_engine'))

        # Engine selection
        ctk.CTkLabel(tab, text=_translator.t('settings.engine_label'),
                    font=("Arial", 12, "bold")).pack(pady=(10, 5), anchor="w")

        self.engine_var = ctk.StringVar(value=self.config.get('engine', 'local'))
        engines = ['local', 'openai', 'deepgram']
        for eng in engines:
            ctk.CTkRadioButton(
                tab, text=eng.capitalize(), variable=self.engine_var,
                value=eng
            ).pack(pady=2, anchor="w", padx=20)

        # Model selection (for local)
        ctk.CTkLabel(tab, text=_translator.t('settings.model_label'),
                    font=("Arial", 12, "bold")).pack(pady=(15, 5), anchor="w")

        self.model_var = ctk.StringVar(value=self.config.get('local', {}).get('model', 'tiny'))
        models = ['tiny', 'base', 'small', 'medium', 'large']
        self.model_menu = ctk.CTkOptionMenu(
            tab, values=models, variable=self.model_var,
            command=self._on_model_change
        )
        self.model_menu.pack(pady=5, anchor="w", padx=20)

        # Model warning label (hidden by default)
        self.model_warning = ctk.CTkLabel(
            tab,
            text="",
            font=("Arial", 10),
            text_color="orange",
            wraplength=450
        )
        self.model_warning.pack(pady=(0, 5), anchor="w", padx=20)
        self._update_model_warning(self.model_var.get())

        # Language
        ctk.CTkLabel(tab, text=_translator.t('settings.language_label'),
                    font=("Arial", 12, "bold")).pack(pady=(15, 5), anchor="w")

        self.lang_var = ctk.StringVar(value=self.config.get('local', {}).get('language', 'auto'))
        languages = ['auto', 'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'zh']
        self.lang_menu = ctk.CTkOptionMenu(tab, values=languages, variable=self.lang_var)
        self.lang_menu.pack(pady=5, anchor="w", padx=20)

    def _setup_audio_tab(self):
        """Setup audio configuration tab"""
        tab = self.tabview.tab(_translator.t('settings.tab_audio'))

        # Microphone selection
        ctk.CTkLabel(tab, text=_translator.t('settings.microphone_label'),
                    font=("Arial", 12, "bold")).pack(pady=(10, 5), anchor="w")

        devices = list_input_devices()
        device_names = [f"{d['id']}: {d['name']}" for d in devices]

        current_device = self.config.get('audio', {}).get('sound_device', 'default')
        self.device_var = ctk.StringVar(value=str(current_device))

        self.device_menu = ctk.CTkOptionMenu(tab, values=device_names if device_names else ['default'],
                                            variable=self.device_var)
        self.device_menu.pack(pady=5, anchor="w", padx=20, fill="x")

        # Sample rate
        ctk.CTkLabel(tab, text=_translator.t('settings.sample_rate_label'),
                    font=("Arial", 12, "bold")).pack(pady=(15, 5), anchor="w")

        self.sr_var = ctk.StringVar(value=str(self.config.get('audio', {}).get('sample_rate', 48000)))
        sample_rates = ['16000', '44100', '48000']
        self.sr_menu = ctk.CTkOptionMenu(tab, values=sample_rates, variable=self.sr_var)
        self.sr_menu.pack(pady=5, anchor="w", padx=20)

    def _setup_behavior_tab(self):
        """Setup behavior configuration tab"""
        tab = self.tabview.tab(_translator.t('settings.tab_behavior'))

        # Stop on keypress
        self.stop_on_keypress_var = ctk.BooleanVar(
            value=self.config.get('behavior', {}).get('stop_on_any_keypress', True)
        )
        ctk.CTkCheckBox(
            tab,
            text=_translator.t('settings.stop_on_keypress'),
            variable=self.stop_on_keypress_var
        ).pack(pady=10, anchor="w")

        # Add trailing space
        self.add_space_var = ctk.BooleanVar(
            value=self.config.get('typing', {}).get('add_trailing_space', True)
        )
        ctk.CTkCheckBox(
            tab,
            text=_translator.t('settings.add_trailing_space'),
            variable=self.add_space_var
        ).pack(pady=10, anchor="w")

        # Remove trailing period
        self.remove_period_var = ctk.BooleanVar(
            value=self.config.get('typing', {}).get('remove_trailing_period', False)
        )
        ctk.CTkCheckBox(
            tab,
            text=_translator.t('settings.remove_trailing_period'),
            variable=self.remove_period_var
        ).pack(pady=10, anchor="w")

        # Clipboard integration
        self.clipboard_var = ctk.BooleanVar(
            value=self.config.get('clipboard', {}).get('enabled', True)
        )
        ctk.CTkCheckBox(
            tab,
            text=_translator.t('settings.clipboard_enabled'),
            variable=self.clipboard_var
        ).pack(pady=10, anchor="w")

        # Auto-clear on start
        self.auto_clear_var = ctk.BooleanVar(
            value=self.config.get('behavior', {}).get('auto_clear_on_start', False)
        )
        ctk.CTkCheckBox(
            tab,
            text=_translator.t('settings.auto_clear_on_start'),
            variable=self.auto_clear_var
        ).pack(pady=10, anchor="w")

        # Separator
        ctk.CTkLabel(
            tab,
            text="",
            height=1
        ).pack(pady=15)

        # Advanced editors section
        ctk.CTkLabel(
            tab,
            text=_translator.t('settings.advanced_editors_label'),
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10), anchor="w")

        # Voice Commands editor button
        ctk.CTkButton(
            tab,
            text=_translator.t('settings.edit_voice_commands'),
            command=self._open_voice_commands,
            width=200,
            fg_color="darkblue",
            hover_color="blue"
        ).pack(pady=5, anchor="w", padx=20)

        # Word Replacements editor button
        ctk.CTkButton(
            tab,
            text=_translator.t('settings.edit_word_replacements'),
            command=self._open_word_replacements,
            width=200,
            fg_color="darkblue",
            hover_color="blue"
        ).pack(pady=5, anchor="w", padx=20)

        # Templates editor button
        ctk.CTkButton(
            tab,
            text=_translator.t('settings.edit_templates'),
            command=self._open_templates,
            width=200,
            fg_color="darkblue",
            hover_color="blue"
        ).pack(pady=5, anchor="w", padx=20)

    def _on_model_change(self, value):
        """Handle model selection change"""
        self._update_model_warning(value)

    def _update_model_warning(self, model_name):
        """Show/hide performance warning based on model and device"""
        device = self.config.get('local', {}).get('device', 'cpu')
        slow_models = {'medium', 'large'}
        if model_name in slow_models and device == 'cpu':
            self.model_warning.configure(
                text=f"'{model_name}' on CPU may be too slow for real-time dictation. "
                     f"Consider 'tiny' or 'base' for CPU, or use CUDA for larger models."
            )
        else:
            self.model_warning.configure(text="")

    def _open_voice_commands(self):
        """Open Voice Commands editor dialog"""
        VoiceCommandsDialog(self.parent)

    def _open_word_replacements(self):
        """Open Word Replacements editor dialog"""
        WordReplacementsDialog(self.parent)

    def _open_templates(self):
        """Open Templates editor dialog"""
        TemplatesDialog(self.parent)

    def _setup_hotkey_tab(self):
        """Setup hotkey configuration tab"""
        tab = self.tabview.tab(_translator.t('settings.tab_hotkey'))

        ctk.CTkLabel(tab, text=_translator.t('settings.hotkey_label'),
                    font=("Arial", 12, "bold")).pack(pady=(10, 5), anchor="w")

        self.hotkey_entry = ctk.CTkEntry(tab, width=200)
        self.hotkey_entry.insert(0, self.config.get('hotkey', 'ctrl+a'))
        self.hotkey_entry.pack(pady=5, anchor="w", padx=20)

        ctk.CTkLabel(
            tab,
            text=_translator.t('settings.hotkey_help'),
            font=("Arial", 10),
            text_color="gray"
        ).pack(pady=5, anchor="w", padx=20)

    def _save(self):
        """Save settings"""
        # Update config
        self.config['engine'] = self.engine_var.get()
        self.config['local']['model'] = self.model_var.get()
        self.config['local']['language'] = self.lang_var.get()
        self.config['audio']['sample_rate'] = int(self.sr_var.get())
        self.config['behavior']['stop_on_any_keypress'] = self.stop_on_keypress_var.get()
        self.config['behavior']['auto_clear_on_start'] = self.auto_clear_var.get()
        self.config['typing']['add_trailing_space'] = self.add_space_var.get()
        self.config['typing']['remove_trailing_period'] = self.remove_period_var.get()
        self.config['clipboard']['enabled'] = self.clipboard_var.get()
        self.config['hotkey'] = self.hotkey_entry.get()

        requested_model = self.model_var.get()

        # Preserve sub-dialog changes (word replacements, voice commands, templates)
        # that may have been saved directly to the engine while this dialog was open.
        for key in ('word_replacements', 'voice_commands', 'templates'):
            if key in self.engine.config:
                self.config[key] = self.engine.config[key]

        # Apply to engine (may revert model on failure)
        self.engine.update_config(self.config)

        # Check if model was reverted due to load failure
        actual_model = self.engine.config.get('local', {}).get('model', requested_model)
        if actual_model != requested_model:
            messagebox.showwarning(
                _translator.t('settings.success_title'),
                f"Failed to load model '{requested_model}'. "
                f"Reverted to '{actual_model}'.\n\n"
                f"Larger models may require more RAM or GPU (CUDA) support."
            )
        else:
            messagebox.showinfo(_translator.t('settings.success_title'),
                               _translator.t('settings.success_message'))

        self.destroy()
