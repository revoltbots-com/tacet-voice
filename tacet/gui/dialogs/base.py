"""
Base Dialog Class

Shared base class for all application dialogs.
"""

import customtkinter as ctk
from tacet.gui.utils.icons import set_dialog_icon


class BaseDialog(ctk.CTkToplevel):
    """
    Base class for all application dialogs.

    Provides common functionality:
    - Icon setting
    - Modal behavior
    - Centering on parent
    """

    def __init__(self, parent, title, size="500x400", resizable=False):
        """
        Initialize BaseDialog.

        Args:
            parent: Parent window
            title: Dialog title
            size: Window size as "WIDTHxHEIGHT"
            resizable: Whether window is resizable
        """
        super().__init__(parent)
        self.title(title)
        self.geometry(size)
        self.resizable(resizable, resizable)

        # Set window icon
        set_dialog_icon(self)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.center_on_parent(parent)

    def center_on_parent(self, parent):
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
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        self.geometry(f"+{x}+{y}")
