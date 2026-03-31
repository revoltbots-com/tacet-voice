"""
Text Editor Dialog Component

Modal popup dialog for editing multi-line text.
"""

import customtkinter as ctk
from tacet.gui.core.translation import get_translator

_translator = get_translator()


class TextEditorDialog(ctk.CTkToplevel):
    """
    Popup dialog for multi-line text editing.

    Used by Templates dialog to edit template content.
    """

    def __init__(self, parent, title: str, initial_text: str, on_save):
        """
        Initialize text editor dialog.

        Args:
            parent: Parent window
            title: Dialog title
            initial_text: Initial text content
            on_save: Callback function(new_text) called when user saves
        """
        super().__init__(parent)

        self.on_save = on_save

        # Dialog configuration
        self.title(title)
        self.geometry("600x400")
        self.resizable(True, True)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self._center_on_parent(parent)

        # Create UI
        self._create_widgets(initial_text)

    def _center_on_parent(self, parent):
        """Center dialog on parent window"""
        self.update_idletasks()

        # Get parent position and size
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Get dialog size
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

    def _create_widgets(self, initial_text):
        """Create dialog widgets"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Label
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('templates_dialog.edit_text_label'),
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10), anchor="w")

        # Text area
        self.text_box = ctk.CTkTextbox(
            main_frame,
            font=("Arial", 11),
            wrap="word"
        )
        self.text_box.pack(fill="both", expand=True, pady=(0, 15))

        # Insert initial text
        self.text_box.insert("1.0", initial_text)

        # Focus text area
        self.text_box.focus_set()

        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        # Save button
        ctk.CTkButton(
            button_frame,
            text=_translator.t('buttons.save'),
            command=self._save,
            width=100
        ).pack(side="left", padx=(0, 5))

        # Cancel button
        ctk.CTkButton(
            button_frame,
            text=_translator.t('buttons.cancel'),
            command=self.destroy,
            width=100,
            fg_color="gray"
        ).pack(side="left")

    def _save(self):
        """Save and close dialog"""
        # Get text content
        new_text = self.text_box.get("1.0", "end-1c")

        # Call save callback
        if self.on_save:
            self.on_save(new_text)

        # Close dialog
        self.destroy()
