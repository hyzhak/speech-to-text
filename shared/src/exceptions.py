"""Shared Exception Classes

This module defines custom exception classes used throughout the
modular speech-to-text system for consistent error handling.
"""

from typing import Dict, Any, Optional


class STTException(Exception):
    """Base exception class for speech-to-text system errors."""

    def __init__(
        self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format for serialization."""
        return {
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class AudioFormatError(STTException):
    """Exception raised for audio format related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUDIO_FORMAT_ERROR", details)


class ModelLoadError(STTException):
    """Exception raised when ML model fails to load."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "MODEL_LOAD_ERROR", details)


class TranscriptionError(STTException):
    """Exception raised during transcription processing."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "TRANSCRIPTION_ERROR", details)


class ValidationError(STTException):
    """Exception raised for input validation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class ConfigurationError(STTException):
    """Exception raised for configuration related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)
