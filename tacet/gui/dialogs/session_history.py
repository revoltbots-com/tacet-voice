"""
Session History Dialog

View and restore previous transcription sessions.
"""

import customtkinter as ctk
from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon

_translator = get_translator()


class SessionHistoryDialog(ctk.CTkToplevel):
    def __init__(self, parent, restore_callback=None):
        """
        Initialize session history dialog.

        Args:
            parent: Parent window
            restore_callback: Optional callback(text) to restore session text to main window
        """
        super().__init__(parent)
        self.parent = parent
        self.restore_callback = restore_callback

        self.title(_translator.t('session_history_dialog.title'))
        self.geometry("700x500")
        self.resizable(True, True)

        set_dialog_icon(self)
        self.transient(parent)
        self.grab_set()

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('session_history_dialog.title'),
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 15))

        # Sessions list
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=350)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Load sessions
        if hasattr(parent.engine, 'session_history'):
            sessions = parent.engine.session_history.load_sessions()
            for session in sessions:
                self._create_session_row(scroll_frame, session)
        else:
            ctk.CTkLabel(
                scroll_frame,
                text=_translator.t('session_history_dialog.no_sessions'),
                font=("Arial", 12),
                text_color="gray"
            ).pack(pady=20)

        # Close button
        ctk.CTkButton(
            main_frame,
            text=_translator.t('buttons.close'),
            command=self.destroy,
            width=100
        ).pack()

    def _create_session_row(self, parent, session):
        """Create a row for a session"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5, padx=5)

        # Session info
        timestamp = session.get('timestamp', 'Unknown')
        word_count = session.get('word_count', 0)

        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)

        ctk.CTkLabel(
            info_frame,
            text=timestamp,
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=f"{word_count} words",
            font=("Arial", 9),
            text_color="gray"
        ).pack(anchor="w")

        # View button
        ctk.CTkButton(
            frame,
            text="View",
            command=lambda: self._view_session(session),
            width=80
        ).pack(side="right", padx=5)

    def _view_session(self, session):
        """View session text in popup dialog"""
        # Extract session data
        text = session.get('text', '')
        timestamp = session.get('timestamp', 'Unknown')
        word_count = session.get('word_count', 0)
        duration = session.get('duration', 0)

        # Create viewer dialog
        viewer = ctk.CTkToplevel(self)
        viewer.title(_translator.t('session_history_dialog.viewer_title'))
        viewer.geometry("700x600")
        viewer.resizable(True, True)

        set_dialog_icon(viewer)
        viewer.transient(self)
        viewer.grab_set()

        # Main frame
        main_frame = ctk.CTkFrame(viewer)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('session_history_dialog.viewer_title'),
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 15))

        # Metadata frame
        metadata_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        metadata_frame.pack(fill="x", pady=(0, 15))

        # Date
        ctk.CTkLabel(
            metadata_frame,
            text=f"Date: {timestamp}",
            font=("Arial", 11)
        ).pack(anchor="w", pady=2)

        # Word count
        ctk.CTkLabel(
            metadata_frame,
            text=f"Words: {word_count}",
            font=("Arial", 11)
        ).pack(anchor="w", pady=2)

        # Duration (if available)
        if duration > 0:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            ctk.CTkLabel(
                metadata_frame,
                text=f"Duration: {minutes}m {seconds}s",
                font=("Arial", 11)
            ).pack(anchor="w", pady=2)

        # Text area (read-only)
        text_label = ctk.CTkLabel(
            main_frame,
            text=_translator.t('session_history_dialog.session_text_label'),
            font=("Arial", 12, "bold")
        )
        text_label.pack(anchor="w", pady=(0, 5))

        text_box = ctk.CTkTextbox(
            main_frame,
            font=("Arial", 11),
            wrap="word"
        )
        text_box.pack(fill="both", expand=True, pady=(0, 15))

        # Insert session text
        text_box.insert("1.0", text)
        text_box.configure(state="disabled")  # Make read-only

        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        # Restore to main window button
        if self.restore_callback:
            def restore_and_close():
                self.restore_callback(text)
                viewer.destroy()

            ctk.CTkButton(
                button_frame,
                text=_translator.t('session_history_dialog.restore_session'),
                command=restore_and_close,
                width=180,
                fg_color="green",
                hover_color="darkgreen"
            ).pack(side="left", padx=5)

        # Copy to clipboard button
        def copy_to_clipboard():
            viewer.clipboard_clear()
            viewer.clipboard_append(text)
            # Show brief confirmation
            copy_btn.configure(text="✓ Copied!")
            viewer.after(1500, lambda: copy_btn.configure(text=_translator.t('buttons.copy')))

        copy_btn = ctk.CTkButton(
            button_frame,
            text=_translator.t('buttons.copy'),
            command=copy_to_clipboard,
            width=100
        )
        copy_btn.pack(side="left", padx=5)

        # Close button
        ctk.CTkButton(
            button_frame,
            text=_translator.t('buttons.close'),
            command=viewer.destroy,
            width=100,
            fg_color="gray"
        ).pack(side="left", padx=5)
