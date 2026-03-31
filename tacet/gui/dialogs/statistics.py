"""
Statistics Dialog

Display usage statistics and time saved metrics.
"""

import customtkinter as ctk
from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon

_translator = get_translator()


class StatisticsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title(_translator.t('usage_stats.dialog_title'))
        self.geometry("450x400")
        self.resizable(False, False)

        set_dialog_icon(self)
        self.transient(parent)
        self.grab_set()

        # Get stats from engine
        if parent.engine and hasattr(parent.engine, 'stats_tracker'):
            stats = parent.engine.stats_tracker.get_stats()
        else:
            stats = {"total_words": 0, "total_sessions": 0, "total_time_seconds": 0, "time_saved_minutes": 0}

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Title
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('usage_stats.title'),
            font=("Arial", 20, "bold")
        ).pack(pady=(0, 20))

        # Stats grid
        stats_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True)

        # Total words
        self._create_stat_row(stats_frame, _translator.t('usage_stats.total_words'),
                             f"{stats['total_words']:,}", 0)

        # Total sessions
        self._create_stat_row(stats_frame, _translator.t('usage_stats.total_sessions'),
                             str(stats['total_sessions']), 1)

        # Time saved
        time_saved_hours = stats['time_saved_minutes'] / 60
        self._create_stat_row(stats_frame, _translator.t('usage_stats.time_saved'),
                             f"{time_saved_hours:.1f} " + _translator.t('usage_stats.hours'), 2)

        # Close button
        ctk.CTkButton(
            main_frame,
            text=_translator.t('buttons.close'),
            command=self.destroy,
            width=100
        ).pack(pady=(20, 0))

    def _create_stat_row(self, parent, label, value, row):
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
