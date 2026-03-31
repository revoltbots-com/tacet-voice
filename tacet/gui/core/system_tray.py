"""
System Tray Icon

System tray integration with status updates and menu.
"""

import os
import threading
from PIL import Image, ImageDraw
import pystray


class TrayIcon:
    """
    System tray icon with status indication and menu.

    Provides quick access to show/hide window, start/stop dictation,
    and quit the application.
    """

    def __init__(self, app):
        """
        Initialize TrayIcon.

        Args:
            app: Main application window (TranscriptionGUI instance)
        """
        self.app = app
        self.icon = None
        self.is_running = False

    def create_icon_image(self, status="idle"):
        """
        Create a simple icon image with status color.

        Args:
            status: Current status ('idle', 'listening', 'transcribing')

        Returns:
            PIL Image for tray icon
        """
        # Status colors
        colors = {
            "idle": "#808080",       # Gray
            "listening": "#4CAF50",  # Green
            "transcribing": "#2196F3"  # Blue
        }

        # Try to load custom favicon first
        try:
            here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            favicon_path = os.path.join(here, "assets", "favicon.png")

            if os.path.exists(favicon_path):
                # Load custom icon
                img = Image.open(favicon_path)

                # Resize to standard tray icon size
                img = img.resize((64, 64), Image.Resampling.LANCZOS)

                # Add status indicator (small colored dot in corner)
                draw = ImageDraw.Draw(img)
                color = colors.get(status, colors["idle"])
                draw.ellipse([44, 44, 60, 60], fill=color)

                return img
        except Exception as e:
            print(f"Could not load custom tray icon: {e}")

        # Fallback: Create simple colored circle
        img = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(img)

        color = colors.get(status, colors["idle"])
        draw.ellipse([8, 8, 56, 56], fill=color, outline='black', width=2)

        return img

    def update_status(self, status):
        """
        Update the tray icon with new status.

        Args:
            status: New status ('idle', 'listening', 'transcribing')
        """
        if self.icon:
            self.icon.icon = self.create_icon_image(status)

    def show_window(self, icon=None, item=None):
        """Show the main window"""
        self.app.after(0, self.app.deiconify)
        self.app.after(0, self.app.lift)
        self.app.after(0, self.app.focus_force)

    def hide_window(self):
        """Hide the main window to tray"""
        self.app.withdraw()

    def toggle_dictation(self, icon=None, item=None):
        """Start/stop dictation from tray menu"""
        if self.app.engine:
            if self.app.engine.is_listening():
                self.app.after(0, self.app._stop_dictation)
            else:
                self.app.after(0, self.app._start_dictation)

    def open_settings(self, icon=None, item=None):
        """Open settings dialog from tray menu"""
        self.app.after(0, self.show_window)
        self.app.after(0, self.app._open_settings)

    def quit_app(self, icon=None, item=None):
        """Quit the application from tray menu"""
        self.app.after(0, self.app._on_closing)

    def create_menu(self):
        """
        Create the system tray menu.

        Returns:
            pystray.Menu instance
        """
        return pystray.Menu(
            pystray.MenuItem("Show", self.show_window, default=True),
            pystray.MenuItem("Start/Stop Dictation", self.toggle_dictation),
            pystray.MenuItem("Settings", self.open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app)
        )

    def start(self):
        """Start the system tray icon"""
        if self.is_running:
            return

        self.is_running = True
        self.icon = pystray.Icon(
            "tacet",
            self.create_icon_image("idle"),
            "Tacet",
            self.create_menu()
        )

        # Run in separate thread
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        """Stop the system tray icon"""
        if self.icon:
            self.icon.stop()
            self.is_running = False
