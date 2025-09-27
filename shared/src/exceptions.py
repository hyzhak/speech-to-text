"""Custom exceptions for the speech-to-text system.

This module defines all custom exception classes used throughout the
modular speech-to-text system for consistent error handling.
"""


class STTError(Exception):
    """Base exception class for all speech-to-text system errors."""

    def __init__(self, message: str, details: dict = None):
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AudioFormatError(STTError):
    """Exception raised for audio format related errors."""

    pass


class ModelLoadError(STTError):
    """Exception raised when model loading fails."""

    pass


class TranscriptionError(STTError):
    """Exception raised when transcription fails."""

    pass


class ValidationError(STTError):
    """Exception raised for validation errors."""

    pass


class ConfigurationError(STTError):
    """Exception raised for configuration errors."""

    pass
