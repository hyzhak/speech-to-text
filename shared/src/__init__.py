"""Shared libraries and interfaces package

This package contains shared data models, interfaces, and utilities
used across all services in the modular speech-to-text system.
"""

from .exceptions import (
    AudioFormatError,
    ConfigurationError,
    ModelLoadError,
    STTError,
    TranscriptionError,
    ValidationError,
)
from .interfaces.audio_format import AudioFormatHandler
from .interfaces.stt_model import SpeechToTextModel
from .mock_stt_model import MockSpeechToTextModel
from .models import AudioRequest, ModelConfig, TranscriptionResult

__all__ = [
    # Data Models
    "AudioRequest",
    "TranscriptionResult",
    "ModelConfig",
    # Exceptions
    "STTError",
    "AudioFormatError",
    "ModelLoadError",
    "TranscriptionError",
    "ValidationError",
    "ConfigurationError",
    # Interfaces
    "SpeechToTextModel",
    "AudioFormatHandler",
    # Implementations
    "MockSpeechToTextModel",
]
