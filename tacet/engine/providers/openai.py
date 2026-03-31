"""
OpenAI Transcription Provider

Uses OpenAI's Whisper API for cloud-based transcription.
"""

from typing import Optional
import requests

from tacet.engine.base import BaseEngine


class OpenAIEngine(BaseEngine):
    """
    OpenAI API transcription engine.

    Uses OpenAI's Whisper API for high-quality cloud transcription.
    Requires an OpenAI API key.
    """

    def __init__(self, base_url: str, model: str, api_key: str):
        """
        Initialize OpenAIEngine.

        Args:
            base_url: OpenAI API base URL (e.g., 'https://api.openai.com/v1')
            model: Model name (e.g., 'whisper-1')
            api_key: OpenAI API key
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    def transcribe(self, wav_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio using OpenAI API.

        Args:
            wav_path: Path to WAV audio file
            language: Optional language code (e.g., 'en', 'es')

        Returns:
            Transcribed text

        Raises:
            requests.HTTPError: If API request fails
        """
        url = f"{self.base_url}/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"model": self.model, "response_format": "json"}

        if language:
            data["language"] = language

        with open(wav_path, "rb") as f:
            files = {"file": ("audio.wav", f, "audio/wav")}
            r = requests.post(url, headers=headers, data=data, files=files, timeout=120)

        r.raise_for_status()
        return (r.json().get("text") or "").strip()

    def __repr__(self) -> str:
        return f"OpenAIEngine(model={self.model})"
