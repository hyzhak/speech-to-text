"""Shared interfaces package

This package contains abstract base classes and interfaces that define
the contracts for different components in the speech-to-text system.
"""

from .stt_model import SpeechToTextModel
from .audio_format import AudioFormatHandler

__all__ = [
    "SpeechToTextModel",
    "AudioFormatHandler"
]