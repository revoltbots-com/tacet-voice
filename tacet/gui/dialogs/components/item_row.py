"""
Item Row Component

Configurable row widget for editor lists.
Supports enabled checkbox, text fields, and action buttons.
"""

import customtkinter as ctk
from typing import Callable, Dict, Optional


class ItemRow(ctk.CTkFrame):
    """
    Configurable row widget for different item types.

    Can display:
    - Optional enabled checkbox
    - Multiple text entry fields
    - Optional edit button
    - Optional delete button
    """

    def __init__(
        self,
        parent,
        item_id: str,
        item_data: Dict,
        config: Dict,
        on_change: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_edit: Optional[Callable] = None
    ):
        """
        Initialize item row.

        Args:
            parent: Parent widget
            item_id: Unique identifier for this item
            item_data: Dictionary of item data
            config: Row configuration dict with:
                - fields: List of {name, label, width, readonly}
                - show_enabled: bool (show enabled checkbox)
                - show_delete: bool (show delete button)
                - show_edit: bool (show edit button)
            on_change: Callback(item_id, data) when data changes
            on_delete: Callback(item_id) when delete clicked
            on_edit: Callback(item_id) when edit clicked
        """
        super().__init__(parent, fg_color="transparent")

        self.item_id = item_id
        self.item_data = item_data.copy()
        self.config = config
        self.on_change = on_change
        self.on_delete = on_delete
        self.on_edit = on_edit

        # Widget references
        self.enabled_var = None
        self.field_widgets = {}

        # Create widgets
        self._create_widgets()

    def _create_widgets(self):
        """Create row widgets"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        current_col = 0

        # Enabled checkbox (optional)
        if self.config.get('show_enabled', False):
            self.enabled_var = ctk.BooleanVar(
                value=self.item_data.get('enabled', True)
            )
            checkbox = ctk.CTkCheckBox(
                self,
                text="",
                variable=self.enabled_var,
                width=30,
                command=self._on_data_changed
            )
            checkbox.grid(row=0, column=current_col, padx=(0, 10), sticky="w")
            current_col += 1

        # Text fields
        fields_frame = ctk.CTkFrame(self, fg_color="transparent")
        fields_frame.grid(row=0, column=current_col, sticky="ew", padx=(0, 10))
        current_col += 1

        for i, field_config in enumerate(self.config.get('fields', [])):
            field_name = field_config['name']
            width = field_config.get('width', 150)
            readonly = field_config.get('readonly', False)

            # Create entry widget
            entry = ctk.CTkEntry(
                fields_frame,
                width=width,
                placeholder_text=field_config.get('label', field_name)
            )
            entry.pack(side="left", padx=(0, 5))

            # Insert initial value
            value = self.item_data.get(field_name, '')
            if value:
                entry.insert(0, str(value))

            # Make readonly if specified
            if readonly:
                entry.configure(state="disabled")
            else:
                # Bind change event
                entry.bind("<FocusOut>", lambda e: self._on_data_changed())
                entry.bind("<Return>", lambda e: self._on_data_changed())

            self.field_widgets[field_name] = entry

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=0, column=current_col, sticky="e")

        # Edit button (optional)
        if self.config.get('show_edit', False) and self.on_edit:
            edit_btn = ctk.CTkButton(
                button_frame,
                text="Edit",
                width=60,
                command=lambda: self.on_edit(self.item_id)
            )
            edit_btn.pack(side="left", padx=2)

        # Delete button (optional)
        if self.config.get('show_delete', False) and self.on_delete:
            delete_btn = ctk.CTkButton(
                button_frame,
                text="Delete",
                width=60,
                fg_color="darkred",
                hover_color="red",
                command=lambda: self.on_delete(self.item_id)
            )
            delete_btn.pack(side="left", padx=2)

    def _on_data_changed(self):
        """Handle data change"""
        if self.on_change:
            data = self.get_data()
            self.on_change(self.item_id, data)

    def get_data(self) -> Dict:
        """
        Get current row data.

        Returns:
            Dictionary of current field values
        """
        data = {'id': self.item_id}

        # Get enabled state
        if self.enabled_var:
            data['enabled'] = self.enabled_var.get()

        # Get field values
        for field_name, widget in self.field_widgets.items():
            data[field_name] = widget.get()

        return data

    def set_data(self, data: Dict):
        """
        Update row data.

        Args:
            data: Dictionary of field values
        """
        self.item_data = data.copy()

        # Update enabled checkbox
        if self.enabled_var and 'enabled' in data:
            self.enabled_var.set(data['enabled'])

        # Update field widgets
        for field_name, widget in self.field_widgets.items():
            if field_name in data:
                widget.delete(0, "end")
                widget.insert(0, str(data[field_name]))
