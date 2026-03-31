"""
Base Engine Interface

Abstract base class for all transcription engines.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseEngine(ABC):
    """
    Abstract base class for transcription engines.

    All transcription providers (Local, OpenAI, Deepgram) must implement
    the transcribe() method defined here.
    """

    @abstractmethod
    def transcribe(self, wav_path: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Transcribe audio from a WAV file.

        Args:
            wav_path: Path to the WAV audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
            **kwargs: Additional provider-specific parameters

        Returns:
            Transcribed text as a string

        Raises:
            Exception: If transcription fails
        """
        pass

    def __repr__(self) -> str:
        """String representation of the engine."""
        return f"{self.__class__.__name__}()"
