"""
About Dialog

Application information and credits.
"""

import os
import webbrowser
import customtkinter as ctk
from PIL import Image

from tacet.gui.core.translation import get_translator
from tacet.gui.utils.icons import set_dialog_icon

_translator = get_translator()


class AboutDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        # Get app info from engine config
        app_info = parent.engine.config.get("app", {})
        app_name = app_info.get("name", "Tacet")
        version = app_info.get("version", "1.0.0")
        author = app_info.get("author", "RevoltBots.com")
        website = app_info.get("website", "https://revoltbots.com/products/tacet?ref=app-tacet")
        github = app_info.get("github", "https://github.com/revoltbots-com/tacet-voice")

        self.title(_translator.t('about.dialog_title'))
        self.geometry("450x480")
        self.resizable(False, False)

        # Set window icon
        set_dialog_icon(self)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # App icon/logo (if available)
        self._display_icon(main_frame)

        # App name
        ctk.CTkLabel(
            main_frame,
            text=app_name,
            font=("Arial", 24, "bold")
        ).pack(pady=(0, 5))

        # Version
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('about.version', version=version),
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=(0, 20))

        # Description
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('about.description'),
            font=("Arial", 11),
            justify="center"
        ).pack(pady=(0, 20))

        # Author/Website with Revolt Bots logo
        author_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        author_frame.pack(pady=(0, 0))

        ctk.CTkLabel(
            author_frame,
            text=_translator.t('about.made_by'),
            font=("Arial", 10, "bold")
        ).pack()

        # Revolt Bots logo
        self._display_revoltbots_logo(author_frame, website)

        author_link = ctk.CTkLabel(
            author_frame,
            text=author,
            font=("Arial", 12, "bold"),
            text_color="#1f6aa5",
            cursor="hand2"
        )
        author_link.pack()
        author_link.bind("<Button-1>", lambda e: self._open_url(website))

        # GitHub
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('about.github_label'),
            font=("Arial", 10, "bold")
        ).pack(pady=(15, 0))

        github_link = ctk.CTkLabel(
            main_frame,
            text=_translator.t('about.github_link'),
            font=("Arial", 11),
            text_color="#1f6aa5",
            cursor="hand2"
        )
        github_link.pack()
        github_link.bind("<Button-1>", lambda e: self._open_url(github))

        # Credits
        credits_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        credits_frame.pack(pady=(20, 0), fill="x")

        ctk.CTkLabel(
            credits_frame,
            text=_translator.t('about.built_with'),
            font=("Arial", 10, "bold")
        ).pack()

        ctk.CTkLabel(
            credits_frame,
            text=_translator.t('about.credits'),
            font=("Arial", 9),
            text_color="gray",
            justify="center"
        ).pack(pady=(5, 0))

        # License
        ctk.CTkLabel(
            main_frame,
            text=_translator.t('about.license'),
            font=("Arial", 9),
            text_color="gray"
        ).pack(pady=(15, 0))

        # Close button
        ctk.CTkButton(
            main_frame,
            text=_translator.t('buttons.close'),
            command=self.destroy,
            width=100
        ).pack(pady=(20, 0))

    def _display_icon(self, parent_frame):
        """Display app logo in About dialog (uses icon.png)"""
        try:
            here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            icon_path = os.path.join(here, "assets", "icon.png")

            # Check if logo exists
            if not os.path.exists(icon_path):
                return

            # Load and display logo
            pil_image = Image.open(icon_path)
            pil_image = pil_image.resize((64, 64), Image.Resampling.LANCZOS)

            # Convert to CTkImage
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(64, 64))

            # Display in label
            icon_label = ctk.CTkLabel(parent_frame, image=ctk_image, text="")
            icon_label.pack(pady=(0, 15))

        except Exception as e:
            print(f"Warning: Could not display logo in About dialog: {e}")

    def _display_revoltbots_logo(self, parent_frame, website):
        """Display Revolt Bots logo in About dialog"""
        try:
            here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            logo_path = os.path.join(here, "assets", "revoltbots.png")

            if not os.path.exists(logo_path):
                return

            pil_image = Image.open(logo_path)
            pil_image = pil_image.resize((48, 48), Image.Resampling.LANCZOS)

            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(48, 48))

            logo_label = ctk.CTkLabel(parent_frame, image=ctk_image, text="", cursor="hand2")
            logo_label.pack(pady=(5, 5))
            logo_label.bind("<Button-1>", lambda e: self._open_url(website))

        except Exception as e:
            print(f"Warning: Could not display Revolt Bots logo: {e}")

    def _open_url(self, url):
        """Open URL in browser"""
        webbrowser.open(url)
