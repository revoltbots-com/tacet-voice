"""
Main GUI Application

Transcription GUI application window.
"""

import os
import sys
import queue
import threading
import subprocess
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
from pynput import keyboard as kb

from tacet.engine.dictation import DictationEngine
from tacet.engine.utils.audio import list_input_devices
from tacet.gui.core.translation import get_translator
from tacet.gui.core.system_tray import TrayIcon
from tacet.gui.dialogs import (
    SettingsDialog, VoiceCommandsDialog, WordReplacementsDialog,
    TemplatesDialog, SessionHistoryDialog, StatisticsDialog,
    AboutDialog, ShortcutsDialog, ExportDialog
)
from tacet.gui.utils import (
    IS_MAC, CTRL_SYMBOL, normalize_shortcut,
    enable_auto_start, disable_auto_start
)

_translator = get_translator()


class TranscriptionGUI(ctk.CTk):
    """Main application window for Tacet"""

    def __init__(self):
        super().__init__()

        # Set application icon
        self._set_window_icon()

        # Queue for thread-safe UI updates
        self.ui_queue = queue.Queue()
        self.final_text_end = "1.0"

        # Initialize engine
        here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(here, "config.json")

        try:
            self.engine = DictationEngine(
                config_path=config_path,
                callbacks={
                    'on_status_change': lambda s: self.ui_queue.put(("status", s)),
                    'on_preview_update': lambda t: self.ui_queue.put(("preview", t)),
                    'on_final_text': lambda t: self.ui_queue.put(("final", t)),
                    'on_error': lambda e: self.ui_queue.put(("error", e)),
                }
            )
        except Exception as e:
            print(f"Failed to initialize engine: {repr(e)}")
            self.engine = None

        # Start dictation loop
        if self.engine:
            self.engine.start()

        # Load UI language from config
        if self.engine:
            ui_language = self.engine.config.get("gui", {}).get("ui_language", "en")
            _translator.set_language(ui_language)

        # Set window title (after language is loaded)
        self.title(_translator.t('main_window.title'))

        # Set window size
        if self.engine:
            window_width = self.engine.config.get("gui", {}).get("window_width", 850)
            window_height = self.engine.config.get("gui", {}).get("window_height", 750)
            self.geometry(f"{window_width}x{window_height}")
        else:
            self.geometry("850x750")

        self.minsize(800, 700)

        # Create UI
        self._create_widgets()
        self._create_menu_bar()
        self._setup_keyboard_shortcuts()

        # Start hotkey listener
        if self.engine:
            self._start_hotkey_listener()

        # Initialize system tray
        self.tray_icon = None
        if self.engine:
            minimize_to_tray = self.engine.config.get("gui", {}).get("minimize_to_tray", True)
            if minimize_to_tray:
                self.tray_icon = TrayIcon(self)
                self.tray_icon.start()

        # Start queue processing
        self.process_ui_queue()

        # Handle window close and minimize
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.bind("<Unmap>", self._on_minimize)

    def _set_window_icon(self):
        """Set the application window icon"""
        try:
            here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            assets_dir = os.path.join(here, "assets")
            favicon_png_path = os.path.join(assets_dir, "favicon.png")
            favicon_ico_path = os.path.join(assets_dir, "favicon.ico")

            if not os.path.exists(favicon_png_path):
                return

            if not os.path.exists(favicon_ico_path):
                try:
                    img = Image.open(favicon_png_path)
                    img.save(favicon_ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
                except Exception as e:
                    print(f"Warning: Could not convert favicon: {e}")
                    return

            if os.path.exists(favicon_ico_path):
                self.iconbitmap(favicon_ico_path)

        except Exception as e:
            print(f"Warning: Could not set window icon: {e}")

    def _create_widgets(self):
        """Create all UI widgets"""
        # Top frame - Status and controls
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Status indicator
        status_frame = ctk.CTkFrame(top_frame)
        status_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(status_frame, text=_translator.t('main_window.status_label'),
                    font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))

        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text=_translator.t('main_window.status_idle'),
            font=("Arial", 12),
            text_color="gray"
        )
        self.status_indicator.pack(side="left")

        # Microphone selection
        mic_frame = ctk.CTkFrame(top_frame)
        mic_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(mic_frame, text=_translator.t('main_window.microphone'),
                    font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))

        devices = list_input_devices()
        device_options = [f"[{d['id']}] {d['name']}" for d in devices]

        self.device_var = ctk.StringVar()
        current_device = self.engine.config.get("audio", {}).get("sound_device", 0) if self.engine else 0

        default_option = device_options[0] if device_options else "No devices"
        for opt in device_options:
            if opt.startswith(f"[{current_device}]"):
                default_option = opt
                break

        self.device_var.set(default_option)

        self.device_menu = ctk.CTkOptionMenu(
            mic_frame,
            variable=self.device_var,
            values=device_options if device_options else ["No devices"],
            command=self._on_device_change,
            width=400
        )
        self.device_menu.pack(side="left")

        # UI Language selection
        lang_frame = ctk.CTkFrame(top_frame)
        lang_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(lang_frame, text=_translator.t('main_window.ui_language'),
                    font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))

        available_languages = _translator.get_available_languages()
        lang_options = [f"{name} ({code})" for code, name in available_languages.items()]

        self.ui_lang_var = ctk.StringVar()
        current_lang = self.engine.config.get("gui", {}).get("ui_language", "en") if self.engine else "en"

        # Find current language option
        default_lang = lang_options[0] if lang_options else "English (en)"
        for opt in lang_options:
            if f"({current_lang})" in opt:
                default_lang = opt
                break

        self.ui_lang_var.set(default_lang)

        self.lang_menu = ctk.CTkOptionMenu(
            lang_frame,
            variable=self.ui_lang_var,
            values=lang_options,
            command=self._on_ui_language_change,
            width=200
        )
        self.lang_menu.pack(side="left")

        # Start/Stop button
        button_frame = ctk.CTkFrame(top_frame)
        button_frame.pack(fill="x", pady=10)

        self.start_stop_btn = ctk.CTkButton(
            button_frame,
            text=_translator.t('main_window.start_dictation'),
            command=self._toggle_dictation,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="green"
        )
        self.start_stop_btn.pack(fill="x", pady=(0, 5))

        # Transcription text area
        text_frame = ctk.CTkFrame(self)
        text_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self.text_area = ctk.CTkTextbox(text_frame, font=("Arial", 12))
        self.text_area.pack(fill="both", expand=True)

        # Configure text tags for preview styling
        self.text_area.tag_config("preview_tag", foreground="gray")

    def _create_menu_bar(self):
        """Create menu bar"""
        # Note: CustomTkinter doesn't support native menu bars
        # Create a button-based menu instead
        menu_frame = ctk.CTkFrame(self)
        menu_frame.pack(fill="x", padx=20, pady=(0, 10))

        buttons = [
            (_translator.t('buttons.settings'), self._open_settings),
            (_translator.t('buttons.sessions') if _translator.t('buttons.sessions') != 'buttons.sessions' else 'Sessions', self._open_session_history),
            (_translator.t('buttons.stats'), self._open_statistics),
            (_translator.t('buttons.export'), self._open_export),
            (_translator.t('buttons.about'), self._open_about),
        ]

        for text, command in buttons:
            ctk.CTkButton(menu_frame, text=text, command=command, width=100).pack(side="left", padx=5)

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        shortcuts = {
            f"<{CTRL_SYMBOL}-s>": self._save_text,
            f"<{CTRL_SYMBOL}-o>": self._open_settings,
            f"<{CTRL_SYMBOL}-e>": self._open_export,
        }

        for shortcut, command in shortcuts.items():
            normalized = normalize_shortcut(shortcut)
            if normalized:
                self.bind(normalized, lambda e, cmd=command: cmd())

    def _start_hotkey_listener(self):
        """Start global hotkey listener"""
        if not self.engine:
            return

        hotkey = self.engine.get_hotkey()

        def on_activate():
            self.engine.toggle_listening()

        try:
            self.hotkey_listener = kb.GlobalHotKeys({hotkey: on_activate})
            self.hotkey_listener.start()
        except Exception as e:
            print(f"Failed to start hotkey listener: {e}")

    def _toggle_dictation(self):
        """Toggle dictation on/off"""
        if not self.engine:
            return

        if self.engine.is_listening():
            self._stop_dictation()
        else:
            self._start_dictation()

    def _start_dictation(self):
        """Start dictation"""
        if self.engine:
            self.engine.start_listening()

    def _stop_dictation(self):
        """Stop dictation"""
        if self.engine:
            self.engine.stop_listening()

    def _on_device_change(self, selection):
        """Handle microphone device change"""
        if not self.engine:
            return

        # Extract device ID from selection
        try:
            device_id = int(selection.split("]")[0].split("[")[1])
            self.engine.set_device(device_id)
        except Exception as e:
            print(f"Failed to change device: {e}")

    def _on_ui_language_change(self, selection):
        """Handle UI language change"""
        if not self.engine:
            return

        # Extract language code from selection "Language Name (code)"
        try:
            lang_code = selection.split("(")[1].split(")")[0]

            # Check if language actually changed
            current_lang = self.engine.config.get("gui", {}).get("ui_language", "en")
            if lang_code == current_lang:
                return

            # Update config
            if "gui" not in self.engine.config:
                self.engine.config["gui"] = {}
            self.engine.config["gui"]["ui_language"] = lang_code

            # Save config
            self.engine.save_config()

            # Update translator for the dialog
            _translator.set_language(lang_code)

            # Ask user if they want to restart
            restart = messagebox.askyesno(
                _translator.t('ui_language_change.changed_title'),
                _translator.t('ui_language_change.changed_msg', language=selection)
            )

            if restart:
                self._restart_application()
        except Exception as e:
            print(f"Failed to change UI language: {e}")
            messagebox.showerror("Error", f"Failed to change language: {e}")

    def _restart_application(self):
        """Restart the application"""
        try:
            # Shutdown engine gracefully
            if self.engine:
                self.engine.shutdown()

            # Get the Python executable and script path
            python = sys.executable
            script = os.path.abspath(sys.argv[0])

            # Close this window
            self.destroy()

            # Start new instance
            if script.endswith('.py'):
                # Running as script
                subprocess.Popen([python, script])
            else:
                # Running as executable (frozen)
                subprocess.Popen([sys.executable])

            # Exit current process
            sys.exit(0)
        except Exception as e:
            print(f"Failed to restart application: {e}")
            messagebox.showerror("Restart Failed", f"Could not restart application: {e}")

    def process_ui_queue(self):
        """Process UI update queue"""
        try:
            while not self.ui_queue.empty():
                msg_type, data = self.ui_queue.get_nowait()

                if msg_type == "status":
                    self._update_status(data)
                elif msg_type == "preview":
                    self._update_preview(data)
                elif msg_type == "final":
                    self._commit_final(data)
                elif msg_type == "error":
                    self._show_error(data)

        except Exception as e:
            print(f"Queue processing error: {e}")

        # Schedule next check
        self.after(50, self.process_ui_queue)

    def _update_status(self, status):
        """Update status indicator"""
        status_map = {
            "idle": (_translator.t('main_window.status_idle'), "gray"),
            "listening": (_translator.t('main_window.status_listening'), "green"),
            "transcribing": (_translator.t('main_window.status_transcribing'), "blue"),
        }

        text, color = status_map.get(status, ("Unknown", "gray"))
        self.status_indicator.configure(text=text, text_color=color)

        # Update button based on whether dictation is active
        # Button should show "Stop" for both listening and transcribing states
        if status in ("listening", "transcribing"):
            self.start_stop_btn.configure(
                text=_translator.t('main_window.stop_dictation'),
                fg_color="red"
            )
        else:
            self.start_stop_btn.configure(
                text=_translator.t('main_window.start_dictation'),
                fg_color="green"
            )

        # Update tray icon
        if self.tray_icon:
            self.tray_icon.update_status(status)

    def _update_preview(self, text):
        """Update live preview text (gray interim transcription)"""
        # Delete old preview: everything from final_text_end to end
        self.text_area.delete(self.final_text_end, "end")

        # Insert new preview text at the end
        preview_start = self.text_area.index(self.final_text_end)
        self.text_area.insert("end", text)
        preview_end = self.text_area.index("end-1c")

        # Apply gray color tag to preview text
        self.text_area.tag_add("preview_tag", preview_start, preview_end)

        # Auto-scroll to show latest text
        self.text_area.see("end")

    def _commit_final(self, text):
        """Commit final transcribed text (replaces preview with black text)"""
        # Delete preview: everything from final_text_end to end
        self.text_area.delete(self.final_text_end, "end")

        # Insert final text (black, no tag) with trailing space
        self.text_area.insert("end", text + " ")

        # Update boundary marker to end of final text
        self.final_text_end = self.text_area.index("end-1c")

        # Auto-scroll to show latest text
        self.text_area.see("end")

    def _show_error(self, error):
        """Show error message"""
        messagebox.showerror("Error", error)

    def _save_text(self):
        """Save transcribed text to file"""
        # Get final text only (excludes gray preview)
        text = self.text_area.get("1.0", self.final_text_end)

        if not text.strip():
            messagebox.showwarning("No Text", "No transcription to save!")
            return

        # Open file save dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if not file_path:
            return  # User cancelled

        # Save to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text.strip())
            messagebox.showinfo("Saved", f"Transcription saved successfully!\n\nFile: {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{e}")

    def _open_settings(self):
        """Open settings dialog"""
        if self.engine:
            SettingsDialog(self, self.engine)

    def _open_statistics(self):
        """Open statistics dialog"""
        StatisticsDialog(self)

    def _open_session_history(self):
        """Open session history dialog"""
        # Define restore callback to insert session text into main window
        def restore_session_text(text):
            # Insert text at end of current text
            self.text_area.insert("end", "\n\n" + text)
            # Update final_text_end marker
            self.final_text_end = self.text_area.index("end-1c")
            # Auto-scroll to show restored text
            self.text_area.see("end")

        SessionHistoryDialog(self, restore_callback=restore_session_text)

    def _open_export(self):
        """Open export dialog"""
        text = self.text_area.get("1.0", "end-1c")
        ExportDialog(self, text)

    def _open_about(self):
        """Open about dialog"""
        AboutDialog(self)

    def _on_minimize(self, event):
        """Handle window minimize"""
        if self.tray_icon and event.widget == self:
            self.withdraw()

    def _on_closing(self):
        """Handle window close"""
        if self.engine:
            self.engine.shutdown()

        if self.tray_icon:
            self.tray_icon.stop()

        self.destroy()


def main():
    """Main entry point"""
    # Set appearance mode and theme
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    # Create and run app
    app = TranscriptionGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
