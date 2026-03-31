"""
Statistics Dialog

Display usage statistics and time saved metrics.
"""

import customtkinter as ctk
from tkinter import messagebox
from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon

_translator = get_translator()


class StatisticsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title(_translator.t('usage_stats.dialog_title'))
        self.geometry("450x400")
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
            text=_translator.t('usage_stats.header'),
            font=("Arial", 20, "bold")
        ).pack(pady=(0, 20))

        # Stats grid
        self.stats_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.stats_frame.pack(fill="both", expand=True)

        self._refresh_stats()

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            button_frame,
            text=_translator.t('usage_stats.reset_stats'),
            command=self._reset_stats,
            width=140,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text=_translator.t('buttons.close'),
            command=self.destroy,
            width=100
        ).pack(side="right", padx=5)

    def _refresh_stats(self):
        """Load and display stats"""
        # Clear existing rows
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Get stats from engine
        if self.parent.engine and hasattr(self.parent.engine, 'stats_tracker'):
            stats = self.parent.engine.stats_tracker.get_stats()
        else:
            stats = {"total_words": 0, "total_sessions": 0, "total_time_seconds": 0, "time_saved_minutes": 0}

        # Total words
        self._create_stat_row(self.stats_frame, _translator.t('usage_stats.total_words'),
                             f"{stats['total_words']:,}")

        # Total sessions
        self._create_stat_row(self.stats_frame, _translator.t('usage_stats.total_sessions'),
                             str(stats['total_sessions']))

        # Time saved
        time_saved_hours = stats['time_saved_minutes'] / 60
        self._create_stat_row(self.stats_frame, _translator.t('usage_stats.time_saved'),
                             f"{time_saved_hours:.1f} " + _translator.t('usage_stats.hours'))

    def _reset_stats(self):
        """Reset all usage statistics"""
        confirm = messagebox.askyesno(
            _translator.t('usage_stats.reset_stats'),
            _translator.t('usage_stats.reset_confirm'),
            parent=self
        )
        if confirm and self.parent.engine and hasattr(self.parent.engine, 'stats_tracker'):
            self.parent.engine.stats_tracker.reset()
            self._refresh_stats()
            messagebox.showinfo(
                _translator.t('usage_stats.reset_stats'),
                _translator.t('usage_stats.reset_done'),
                parent=self
            )

    def _create_stat_row(self, parent, label, value):
        """Create a stat row with label and value"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text=label,
            font=("Arial", 12),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            frame,
            text=value,
            font=("Arial", 16, "bold"),
            text_color="#1f6aa5"
        ).pack(side="right")
