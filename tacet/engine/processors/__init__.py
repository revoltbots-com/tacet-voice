"""
Text Processors

Post-processing for transcribed text.
"""

from tacet.engine.processors.voice_commands import VoiceCommandProcessor
from tacet.engine.processors.text_replacement import TextReplacementProcessor
from tacet.engine.processors.auto_punctuation import AutoPunctuationProcessor
from tacet.engine.processors.timestamp import TimestampProcessor
from tacet.engine.processors.template import TemplateProcessor

__all__ = [
    "VoiceCommandProcessor",
    "TextReplacementProcessor",
    "AutoPunctuationProcessor",
    "TimestampProcessor",
    "TemplateProcessor",
]
