"""Shared libraries and interfaces package

This package contains shared data models, interfaces, and utilities
used across all services in the modular speech-to-text system.
"""

from .exceptions import (
    AudioFormatError,
    ConfigurationError,
    ModelLoadError,
    STTBaseError,
    TranscriptionError,
    ValidationError,
)
from .interfaces.audio_format import AudioFormatHandler
from .interfaces.stt_model import SpeechToTextModel
from .models import AudioRequest, ModelConfig, STTError, TranscriptionResult

__all__ = [
    # Data Models
    "AudioRequest",
    "TranscriptionResult",
    "ModelConfig",
    "STTError",
    # Exceptions
    "STTBaseError",
    "AudioFormatError",
    "ModelLoadError",
    "TranscriptionError",
    "ValidationError",
    "ConfigurationError",
    # Interfaces
    "SpeechToTextModel",
    "AudioFormatHandler",
]
