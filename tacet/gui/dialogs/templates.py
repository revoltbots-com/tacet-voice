"""
Templates Dialog

Configure text templates and snippets.
Supports multi-line text editing via popup dialog.
"""

import customtkinter as ctk
from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon
from tacet.gui.dialogs.components import EditorList, ItemRow, TextEditorDialog

_translator = get_translator()


class TemplatesDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config = parent.engine.config.copy()

        self.title(_translator.t('templates_dialog.title'))
        self.geometry("800x600")
        self.resizable(False, False)

        set_dialog_icon(self)
        self.transient(parent)
        self.grab_set()

        # Storage for template text (full text, not just preview)
        self.template_texts = {}

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('templates_dialog.title'),
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 15))

        # Enable checkbox
        self.enabled_var = ctk.BooleanVar(
            value=self.config.get('templates', {}).get('enabled', False)
        )
        ctk.CTkCheckBox(
            main_frame,
            text=_translator.t('templates_dialog.enable'),
            variable=self.enabled_var,
            font=("Arial", 12)
        ).pack(pady=(0, 15), anchor="w")

        # Info label
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('templates_dialog.description'),
            font=("Arial", 11),
            text_color="gray"
        ).pack(pady=(0, 10), anchor="w")

        # Create EditorList for templates
        self.editor_list = EditorList(
            main_frame,
            item_factory=self._create_template_row,
            on_add=self._add_template,
            on_delete=None,  # Handled by ItemRow delete button
            on_reset=self._reset_templates,
            buttons_config={'add': True, 'delete': False, 'reset': True}
        )
        self.editor_list.pack(fill="both", expand=True, pady=(0, 15))

        # Load templates
        self._load_templates()

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

    def _load_templates(self):
        """Load templates from config into editor list"""
        snippets = self.config.get('templates', {}).get('snippets', {})

        for snippet_id, snippet_data in snippets.items():
            trigger = snippet_data.get('trigger', '')
            text = snippet_data.get('text', '')
            enabled = snippet_data.get('enabled', True)

            # Store full text
            self.template_texts[snippet_id] = text

            # Create preview (first 50 chars)
            text_preview = text[:50].replace('\n', ' ') + ('...' if len(text) > 50 else '')

            item_data = {
                'id': snippet_id,
                'trigger': trigger,
                'text_preview': text_preview,
                'enabled': enabled
            }
            self.editor_list.add_item(item_data)

    def _create_template_row(self, item_data):
        """
        Factory method to create ItemRow for a template.

        Args:
            item_data: Dict with keys: id, trigger, text_preview, enabled

        Returns:
            ItemRow widget instance
        """
        # Configure row layout
        row_config = {
            'fields': [
                {'name': 'trigger', 'label': 'Trigger', 'width': 150, 'readonly': False},
                {'name': 'text_preview', 'label': 'Preview', 'width': 300, 'readonly': True}
            ],
            'show_enabled': True,
            'show_delete': True,
            'show_edit': True
        }

        # Create and return ItemRow
        return ItemRow(
            self.editor_list.scroll_frame,
            item_id=item_data['id'],
            item_data=item_data,
            config=row_config,
            on_change=self._on_template_changed,
            on_delete=self._delete_template,
            on_edit=self._edit_template
        )

    def _on_template_changed(self, item_id, data):
        """Handle template data change (trigger or enabled)"""
        # Data is automatically tracked, will be collected on save
        pass

    def _add_template(self):
        """Add new template"""
        # Generate unique ID
        import time
        snippet_id = f"template_{int(time.time() * 1000)}"

        # Default empty template
        text = ""
        self.template_texts[snippet_id] = text

        item_data = {
            'id': snippet_id,
            'trigger': '',
            'text_preview': '(empty)',
            'enabled': True
        }
        self.editor_list.add_item(item_data)

    def _edit_template(self, item_id):
        """Open text editor for template"""
        # Get current text
        current_text = self.template_texts.get(item_id, '')

        # Open TextEditorDialog
        def on_save(new_text):
            # Update stored text
            self.template_texts[item_id] = new_text

            # Update preview in row
            text_preview = new_text[:50].replace('\n', ' ') + ('...' if len(new_text) > 50 else '')

            # Find the widget and update it
            if item_id in self.editor_list.items:
                widget = self.editor_list.items[item_id]
                if hasattr(widget, 'field_widgets') and 'text_preview' in widget.field_widgets:
                    preview_widget = widget.field_widgets['text_preview']
                    preview_widget.configure(state="normal")
                    preview_widget.delete(0, "end")
                    preview_widget.insert(0, text_preview)
                    preview_widget.configure(state="disabled")

        TextEditorDialog(
            self,
            title=_translator.t('templates_dialog.edit_title'),
            initial_text=current_text,
            on_save=on_save
        )

    def _delete_template(self, item_id):
        """Delete template"""
        # Remove from template texts
        if item_id in self.template_texts:
            del self.template_texts[item_id]

        # Remove from editor list
        self.editor_list.remove_item(item_id)

    def _reset_templates(self):
        """Reset templates to defaults"""
        # Get default config
        default_config = self.parent.engine.get_default_config()
        default_snippets = default_config.get('templates', {}).get('snippets', {})

        # Update current config
        self.config['templates']['snippets'] = default_snippets.copy()

        # Clear and reload
        self.template_texts.clear()
        self.editor_list.clear_items()
        self._load_templates()

    def _save(self):
        """Save templates configuration"""
        # Update global enabled flag
        self.config['templates']['enabled'] = self.enabled_var.get()

        # Get all template data from editor list
        items_data = self.editor_list.get_all_items()

        # Build snippets dict
        snippets = {}
        for item_data in items_data:
            snippet_id = item_data['id']
            trigger = item_data.get('trigger', '').strip()

            # Skip templates without trigger
            if not trigger:
                continue

            # Get full text from storage
            text = self.template_texts.get(snippet_id, '')

            snippets[snippet_id] = {
                'trigger': trigger,
                'text': text,
                'enabled': item_data.get('enabled', True)
            }

        # Update config
        self.config['templates']['snippets'] = snippets

        # Save to engine
        self.parent.engine.update_config(self.config)
        self.destroy()
