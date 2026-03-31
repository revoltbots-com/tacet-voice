"""
GUI Dialog Windows

All dialog windows for settings, commands, history, etc.
"""

from tacet.gui.dialogs.base import BaseDialog
from tacet.gui.dialogs.settings import SettingsDialog
from tacet.gui.dialogs.voice_commands import VoiceCommandsDialog
from tacet.gui.dialogs.word_replacements import WordReplacementsDialog
from tacet.gui.dialogs.templates import TemplatesDialog
from tacet.gui.dialogs.session_history import SessionHistoryDialog
from tacet.gui.dialogs.statistics import StatisticsDialog
from tacet.gui.dialogs.about import AboutDialog
from tacet.gui.dialogs.shortcuts import ShortcutsDialog
from tacet.gui.dialogs.export import ExportDialog

__all__ = [
    "BaseDialog",
    "SettingsDialog",
    "VoiceCommandsDialog",
    "WordReplacementsDialog",
    "TemplatesDialog",
    "SessionHistoryDialog",
    "StatisticsDialog",
    "AboutDialog",
    "ShortcutsDialog",
    "ExportDialog",
]
