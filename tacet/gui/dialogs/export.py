"""
Export Dialog

Export transcribed text to various formats.
"""

import os
from tkinter import filedialog
import customtkinter as ctk
from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon

_translator = get_translator()


class ExportDialog(ctk.CTkToplevel):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.text = text

        self.title(_translator.t('export.dialog_title'))
        self.geometry("400x300")
        self.resizable(False, False)

        set_dialog_icon(self)
        self.transient(parent)
        self.grab_set()

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Title
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('export.select_format'),
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))

        # Format options
        ctk.CTkButton(
            main_frame,
            text=_translator.t('export.format_txt'),
            command=lambda: self._export('txt'),
            width=200
        ).pack(pady=10)

        ctk.CTkButton(
            main_frame,
            text=_translator.t('export.format_md'),
            command=lambda: self._export('md'),
            width=200
        ).pack(pady=10)

        ctk.CTkButton(
            main_frame,
            text=_translator.t('export.format_rtf'),
            command=lambda: self._export('rtf'),
            width=200
        ).pack(pady=10)

        # Cancel button
        ctk.CTkButton(
            main_frame,
            text=_translator.t('buttons.cancel'),
            command=self.destroy,
            width=100,
            fg_color="gray"
        ).pack(pady=(20, 0))

    def _export(self, format_type):
        """Export text to file"""
        filetypes = {
            'txt': [('Text files', '*.txt'), ('All files', '*.*')],
            'md': [('Markdown files', '*.md'), ('All files', '*.*')],
            'rtf': [('Rich Text Format', '*.rtf'), ('All files', '*.*')]
        }

        filename = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=filetypes.get(format_type, [('All files', '*.*')])
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    if format_type == 'md':
                        f.write(f"# Transcription\n\n{self.text}")
                    else:
                        f.write(self.text)
                self.destroy()
            except Exception as e:
                print(f"Export failed: {e}")
