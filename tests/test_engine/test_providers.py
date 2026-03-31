"""Tests for transcription providers."""

import pytest


class TestLocalEngine:
    """Test local (faster-whisper) provider."""

    def test_import(self):
        from tacet.engine.providers import LocalEngine
        assert LocalEngine is not None


class TestOpenAIEngine:
    """Test OpenAI API provider."""

    def test_import(self):
        from tacet.engine.providers import OpenAIEngine
        assert OpenAIEngine is not None


class TestDeepgramEngine:
    """Test Deepgram API provider."""

    def test_import(self):
        from tacet.engine.providers import DeepgramEngine
        assert DeepgramEngine is not None


class TestBaseEngine:
    """Test base engine abstract class."""

    def test_import(self):
        from tacet.engine.base import BaseEngine
        assert BaseEngine is not None
