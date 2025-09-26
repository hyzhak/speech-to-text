"""Shared Data Models

This module defines the core data models used across all services in the
modular speech-to-text system. These models ensure consistent data structures
and validation throughout the system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime


@dataclass
class AudioRequest:
    """Request model for audio processing operations."""

    # Supported formats (matching AudioFormatHandler.SUPPORTED_FORMATS)
    SUPPORTED_AUDIO_FORMATS = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]
    SUPPORTED_OUTPUT_FORMATS = ["text", "json"]

    file_path: str
    audio_format: str  # Must be one of SUPPORTED_AUDIO_FORMATS
    output_format: str = "text"
    model_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate the audio request after initialization."""
        if not self.file_path:
            raise ValueError("file_path cannot be empty")

        if self.audio_format.lower() not in self.SUPPORTED_AUDIO_FORMATS:
            raise ValueError(f"Unsupported audio format: {self.audio_format}")

        if self.output_format not in self.SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(f"Unsupported output format: {self.output_format}")


@dataclass
class TranscriptionResult:
    """Result model for speech-to-text transcription operations."""

    text: str
    confidence: float
    processing_time: float
    model_used: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the transcription result after initialization."""
        if not isinstance(self.confidence, (int, float)) or not (
            0.0 <= self.confidence <= 1.0
        ):
            raise ValueError("confidence must be a number between 0.0 and 1.0")

        if (
            not isinstance(self.processing_time, (int, float))
            or self.processing_time < 0
        ):
            raise ValueError("processing_time must be a non-negative number")

        if not self.model_used:
            raise ValueError("model_used cannot be empty")


@dataclass
class ModelConfig:
    """Configuration model for ML model settings."""

    # Supported model types
    SUPPORTED_MODEL_TYPES = ["whisper", "mock"]

    model_type: str  # Must be one of SUPPORTED_MODEL_TYPES
    model_path: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    fallback_enabled: bool = True

    def __post_init__(self):
        """Validate the model configuration after initialization."""
        if self.model_type.lower() not in self.SUPPORTED_MODEL_TYPES:
            raise ValueError(f"Unsupported model type: {self.model_type}")

        if not self.model_path:
            raise ValueError("model_path cannot be empty")


@dataclass
class STTError:
    """Error model for speech-to-text system errors."""

    message: str
    error_code: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the error model after initialization."""
        if not self.message:
            raise ValueError("message cannot be empty")

        if not self.error_code:
            raise ValueError("error_code cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format for serialization."""
        return {
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }
