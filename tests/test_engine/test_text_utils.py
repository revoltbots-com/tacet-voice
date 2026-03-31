"""Tests for text utility functions."""

import pytest


class TestTextUtils:
    """Test text utility imports and availability."""

    def test_import_text_module(self):
        from tacet.engine.utils import text
        assert text is not None

    def test_import_audio_module(self):
        from tacet.engine.utils import audio
        assert audio is not None

    def test_import_keyboard_module(self):
        from tacet.engine.utils import keyboard
        assert keyboard is not None
