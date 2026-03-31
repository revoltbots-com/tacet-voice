"""
Tacet — Speech-to-text dictation, refined.

A professional, cross-platform speech-to-text dictation application.
The name comes from the musical term "tacet" — meaning "be silent" —
the moment before the instrument comes in.
"""

__version__ = "2.0.0"
__author__ = "Revolt Bots LLC"

# Main exports
from tacet.engine.dictation import DictationEngine
from tacet.gui.app import TranscriptionGUI

__all__ = [
    "DictationEngine",
    "TranscriptionGUI",
    "__version__",
    "__author__",
]
