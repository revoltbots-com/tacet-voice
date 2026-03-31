"""
Deepgram Transcription Provider

Uses Deepgram's API for fast, accurate cloud-based transcription.
"""

from typing import Optional
import requests

from tacet.engine.base import BaseEngine


class DeepgramEngine(BaseEngine):
    """
    Deepgram API transcription engine.

    Uses Deepgram's speech-to-text API for fast, accurate transcription.
    Requires a Deepgram API key.
    """

    def __init__(self, api_key: str, model: str = "nova-2"):
        """
        Initialize DeepgramEngine.

        Args:
            api_key: Deepgram API key
            model: Model name (default: 'nova-2')
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.deepgram.com/v1/listen"

    def transcribe(self, wav_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio using Deepgram API.

        Args:
            wav_path: Path to WAV audio file
            language: Optional language code (e.g., 'en', 'es')

        Returns:
            Transcribed text

        Raises:
            requests.HTTPError: If API request fails
        """
        # Build URL with query parameters
        params = {
            "model": self.model,
            "punctuate": "true",
            "smart_format": "true"
        }

        if language:
            params["language"] = language

        # Construct query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.base_url}?{query_string}"

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/wav"
        }

        with open(wav_path, "rb") as f:
            audio_data = f.read()
            r = requests.post(url, headers=headers, data=audio_data, timeout=120)

        r.raise_for_status()
        result = r.json()

        # Extract transcript from Deepgram response
        # Response format: {"results": {"channels": [{"alternatives": [{"transcript": "..."}]}]}}
        try:
            transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
            return transcript.strip()
        except (KeyError, IndexError):
            return ""

    def __repr__(self) -> str:
        return f"DeepgramEngine(model={self.model})"
