"""Tests for text processors."""

import pytest


class TestVoiceCommandProcessor:
    """Test voice command processing."""

    def test_import(self):
        from tacet.engine.processors import VoiceCommandProcessor
        assert VoiceCommandProcessor is not None


class TestTextReplacementProcessor:
    """Test text replacement processing."""

    def test_import(self):
        from tacet.engine.processors import TextReplacementProcessor
        assert TextReplacementProcessor is not None


class TestAutoPunctuationProcessor:
    """Test auto-punctuation processing."""

    def test_import(self):
        from tacet.engine.processors import AutoPunctuationProcessor
        assert AutoPunctuationProcessor is not None


class TestTimestampProcessor:
    """Test timestamp processing."""

    def test_import(self):
        from tacet.engine.processors import TimestampProcessor
        assert TimestampProcessor is not None


class TestTemplateProcessor:
    """Test template processing."""

    def test_import(self):
        from tacet.engine.processors import TemplateProcessor
        assert TemplateProcessor is not None
