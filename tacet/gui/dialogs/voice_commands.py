"""
Voice Commands Dialog

Configure voice commands for dictation control.
"""

import customtkinter as ctk
from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon
from tacet.gui.dialogs.components import EditorList, ItemRow

_translator = get_translator()


class VoiceCommandsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config = parent.engine.config.copy()

        self.title(_translator.t('voice_commands.dialog_title'))
        self.geometry("700x600")
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
            text=_translator.t('voice_commands.title'),
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 15))

        # Info label
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('voice_commands.info_label') if _translator.t('voice_commands.info_label') != 'voice_commands.info_label' else "Enable or disable voice commands:",
            font=("Arial", 11),
            text_color="gray"
        ).pack(pady=(0, 10), anchor="w")

        # Create EditorList for commands
        self.editor_list = EditorList(
            main_frame,
            item_factory=self._create_command_row,
            on_add=None,  # No add button (built-in commands only)
            on_delete=None,  # No delete button (built-in commands only)
            on_reset=self._reset_commands,
            buttons_config={'add': False, 'delete': False, 'reset': True}
        )
        self.editor_list.pack(fill="both", expand=True, pady=(0, 15))

        # Load commands into list
        self._load_commands()

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

    def _load_commands(self):
        """Load voice commands from config into editor list"""
        commands = self.config.get('voice_commands', {}).get('commands', {})

        for phrase, cmd_config in commands.items():
            item_data = {
                'id': phrase,
                'phrase': phrase,
                'action': cmd_config.get('type', 'unknown'),
                'enabled': cmd_config.get('enabled', True)
            }
            self.editor_list.add_item(item_data)

    def _create_command_row(self, item_data):
        """
        Factory method to create ItemRow for a voice command.

        Args:
            item_data: Dict with keys: id, phrase, action, enabled

        Returns:
            ItemRow widget instance
        """
        # Configure row layout
        row_config = {
            'fields': [
                {'name': 'phrase', 'label': 'Phrase', 'width': 250, 'readonly': True},
                {'name': 'action', 'label': 'Action', 'width': 150, 'readonly': True}
            ],
            'show_enabled': True,
            'show_delete': False,
            'show_edit': False
        }

        # Create and return ItemRow
        return ItemRow(
            self.editor_list.scroll_frame,
            item_id=item_data['id'],
            item_data=item_data,
            config=row_config,
            on_change=self._on_command_changed,
            on_delete=None,
            on_edit=None
        )

    def _on_command_changed(self, item_id, data):
        """Handle command data change (enabled/disabled)"""
        # Data is automatically tracked by ItemRow, we'll collect it on save
        pass

    def _reset_commands(self):
        """Reset voice commands to defaults"""
        # Get default commands from engine
        default_config = self.parent.engine.get_default_config()
        default_commands = default_config.get('voice_commands', {}).get('commands', {})

        # Update current config
        self.config['voice_commands']['commands'] = default_commands.copy()

        # Refresh editor list
        self.editor_list.clear_items()
        self._load_commands()

    def _save(self):
        """Save voice commands configuration"""
        # Get all command data from editor list
        items_data = self.editor_list.get_all_items()

        # Update config with enabled states
        commands = self.config.get('voice_commands', {}).get('commands', {})
        for item_data in items_data:
            phrase = item_data['id']
            if phrase in commands:
                commands[phrase]['enabled'] = item_data.get('enabled', True)

        # Save to engine
        self.parent.engine.update_config(self.config)
        self.destroy()
