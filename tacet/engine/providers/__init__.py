"""
Transcription Providers

Supports local (faster-whisper), OpenAI, and Deepgram transcription.
"""

from tacet.engine.providers.local import LocalEngine
from tacet.engine.providers.openai import OpenAIEngine
from tacet.engine.providers.deepgram import DeepgramEngine

__all__ = ["LocalEngine", "OpenAIEngine", "DeepgramEngine"]
