"""
Local Transcription Provider

Uses faster-whisper for local, offline transcription with Whisper models.
"""

from typing import Optional
from faster_whisper import WhisperModel

from tacet.engine.base import BaseEngine


class LocalEngine(BaseEngine):
    """
    Local transcription engine using faster-whisper.

    Provides 100% private, offline transcription using local Whisper models.
    """

    def __init__(self, model_name: str, device: str, compute_type: str):
        """
        Initialize LocalEngine.

        Args:
            model_name: Whisper model name (tiny, base, small, medium, large, etc.)
            device: Device to run on ('cpu', 'cuda', 'auto')
            compute_type: Compute type ('int8', 'float16', 'float32', etc.)
        """
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)

    def transcribe(self, wav_path: str, language: Optional[str] = None, task: str = "transcribe") -> str:
        """
        Transcribe audio using local Whisper model.

        Args:
            wav_path: Path to WAV audio file
            language: Optional language code (e.g., 'en', 'es')
            task: 'transcribe' or 'translate'

        Returns:
            Transcribed text
        """
        segments, _info = self.model.transcribe(
            wav_path,
            language=language,
            task=task,
            beam_size=1,
            vad_filter=False,
        )
        return "".join(seg.text for seg in segments).strip()

    def __repr__(self) -> str:
        return f"LocalEngine(model={self.model_name}, device={self.device})"
