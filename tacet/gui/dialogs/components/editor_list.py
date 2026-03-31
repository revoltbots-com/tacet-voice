"""
Editor List Component

Scrollable list widget with CRUD operations.
Uses factory pattern for creating custom item rows.
"""

import customtkinter as ctk
from typing import Callable, Dict, List, Optional
from tacet.gui.core.translation import get_translator

_translator = get_translator()


class EditorList(ctk.CTkFrame):
    """
    Reusable scrollable list with CRUD operations.

    Features:
    - Scrollable item container
    - Add/Delete/Reset buttons (configurable)
    - Factory pattern for custom row widgets
    - Item lifecycle management
    """

    def __init__(
        self,
        parent,
        item_factory: Callable,
        on_add: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_reset: Optional[Callable] = None,
        buttons_config: Optional[Dict] = None
    ):
        """
        Initialize editor list.

        Args:
            parent: Parent widget
            item_factory: Function(item_data) -> widget to create row
            on_add: Callback() when add button clicked
            on_delete: Callback(item_id) when item deleted
            on_reset: Callback() when reset button clicked
            buttons_config: Dict with {add: bool, delete: bool, reset: bool}
        """
        super().__init__(parent)

        self.item_factory = item_factory
        self.on_add = on_add
        self.on_delete = on_delete
        self.on_reset = on_reset
        self.buttons_config = buttons_config or {'add': True, 'delete': True, 'reset': True}

        # Item storage
        self.items = {}  # item_id -> widget

        # Create widgets
        self._create_widgets()

    def _create_widgets(self):
        """Create list widgets"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Button toolbar (top)
        self._create_toolbar()

        # Scrollable item container
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _create_toolbar(self):
        """Create button toolbar"""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew")

        # Add button
        if self.buttons_config.get('add', True) and self.on_add:
            add_btn = ctk.CTkButton(
                toolbar,
                text=_translator.t('buttons.add') if _translator.t('buttons.add') != 'buttons.add' else "Add",
                width=80,
                command=self.on_add
            )
            add_btn.pack(side="left", padx=(0, 5))

        # Delete button (global - deletes selected)
        if self.buttons_config.get('delete', True):
            delete_btn = ctk.CTkButton(
                toolbar,
                text=_translator.t('buttons.delete_all') if _translator.t('buttons.delete_all') != 'buttons.delete_all' else "Delete All",
                width=100,
                fg_color="darkred",
                hover_color="red",
                command=self._delete_all
            )
            delete_btn.pack(side="left", padx=(0, 5))

        # Reset button
        if self.buttons_config.get('reset', True) and self.on_reset:
            reset_btn = ctk.CTkButton(
                toolbar,
                text=_translator.t('buttons.reset') if _translator.t('buttons.reset') != 'buttons.reset' else "Reset",
                width=80,
                command=self.on_reset
            )
            reset_btn.pack(side="left")

    def add_item(self, data: Dict):
        """
        Add item to list.

        Args:
            data: Item data dictionary (must contain 'id' key)
        """
        item_id = data.get('id', str(len(self.items)))

        # Create row using factory
        row_widget = self.item_factory(data)

        # Add to container
        row_widget.pack(fill="x", pady=2, padx=5)

        # Store reference
        self.items[item_id] = row_widget

    def remove_item(self, item_id: str):
        """
        Remove item from list.

        Args:
            item_id: ID of item to remove
        """
        if item_id in self.items:
            # Destroy widget
            self.items[item_id].destroy()

            # Remove from storage
            del self.items[item_id]

            # Call delete callback
            if self.on_delete:
                self.on_delete(item_id)

    def _delete_all(self):
        """Delete all items"""
        # Get all item IDs
        item_ids = list(self.items.keys())

        # Remove each item
        for item_id in item_ids:
            self.remove_item(item_id)

    def get_all_items(self) -> List[Dict]:
        """
        Get data from all items.

        Returns:
            List of item data dictionaries
        """
        items_data = []

        for item_id, widget in self.items.items():
            # Try to get data from widget
            if hasattr(widget, 'get_data'):
                data = widget.get_data()
                items_data.append(data)
            else:
                # Fallback: just store the ID
                items_data.append({'id': item_id})

        return items_data

    def clear_items(self):
        """Clear all items from list"""
        # Get all widgets
        widgets = list(self.items.values())

        # Destroy all widgets
        for widget in widgets:
            widget.destroy()

        # Clear storage
        self.items.clear()

    def refresh(self, items_data: List[Dict]):
        """
        Refresh list with new data.

        Args:
            items_data: List of item data dictionaries
        """
        # Clear existing items
        self.clear_items()

        # Add new items
        for data in items_data:
            self.add_item(data)

    def get_item_count(self) -> int:
        """
        Get number of items in list.

        Returns:
            Item count
        """
        return len(self.items)
