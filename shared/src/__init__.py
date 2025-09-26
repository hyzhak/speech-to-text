"""Shared libraries and interfaces package

This package contains shared data models, interfaces, and utilities
used across all services in the modular speech-to-text system.
"""

from .models import AudioRequest, TranscriptionResult, ModelConfig, STTError
from .exceptions import (
    STTException,
    AudioFormatError,
    ModelLoadError,
    TranscriptionError,
    ValidationError,
    ConfigurationError
)
from .interfaces.stt_model import SpeechToTextModel
from .interfaces.audio_format import AudioFormatHandler

__all__ = [
    # Data Models
    "AudioRequest",
    "TranscriptionResult", 
    "ModelConfig",
    "STTError",
    
    # Exceptions
    "STTException",
    "AudioFormatError",
    "ModelLoadError",
    "TranscriptionError",
    "ValidationError",
    "ConfigurationError",
    
    # Interfaces
    "SpeechToTextModel",
    "AudioFormatHandler"
]