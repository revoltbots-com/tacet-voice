"""Integration tests — verify all package modules can be imported."""

import pytest


class TestPackageImports:
    """Verify all tacet package modules import successfully."""

    def test_import_root(self):
        import tacet
        assert tacet.__version__ == "2.0.0"

    def test_import_main_classes(self):
        from tacet import DictationEngine, TranscriptionGUI
        assert DictationEngine is not None
        assert TranscriptionGUI is not None

    def test_import_engine(self):
        from tacet.engine import DictationEngine
        assert DictationEngine is not None

    def test_import_engine_base(self):
        from tacet.engine.base import BaseEngine
        assert BaseEngine is not None

    def test_import_providers(self):
        from tacet.engine.providers import LocalEngine, OpenAIEngine, DeepgramEngine
        assert LocalEngine is not None
        assert OpenAIEngine is not None
        assert DeepgramEngine is not None

    def test_import_processors(self):
        from tacet.engine.processors import (
            VoiceCommandProcessor,
            TextReplacementProcessor,
            AutoPunctuationProcessor,
            TimestampProcessor,
            TemplateProcessor,
        )
        assert VoiceCommandProcessor is not None

    def test_import_engine_utils(self):
        from tacet.engine.utils import audio, keyboard, text
        assert audio is not None

    def test_import_tracking(self):
        from tacet.engine.tracking import session, stats
        assert session is not None

    def test_import_gui(self):
        from tacet.gui import TranscriptionGUI
        assert TranscriptionGUI is not None

    def test_import_gui_core(self):
        from tacet.gui.core.translation import get_translator
        assert get_translator is not None

    def test_import_gui_dialogs(self):
        from tacet.gui.dialogs import (
            SettingsDialog,
            VoiceCommandsDialog,
            WordReplacementsDialog,
            TemplatesDialog,
            SessionHistoryDialog,
            StatisticsDialog,
            AboutDialog,
            ShortcutsDialog,
            ExportDialog,
        )
        assert SettingsDialog is not None

    def test_import_gui_dialog_components(self):
        from tacet.gui.dialogs.components import EditorList, ItemRow, TextEditorDialog
        assert EditorList is not None

    def test_import_gui_utils(self):
        from tacet.gui.utils import IS_MAC, IS_WINDOWS, normalize_shortcut
        assert isinstance(IS_MAC, bool)
        assert isinstance(IS_WINDOWS, bool)
