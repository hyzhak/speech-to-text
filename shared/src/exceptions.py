"""Custom exceptions for the modular speech-to-text system.

This module defines all custom exceptions used across the shared libraries
and services to provide consistent error handling and reporting.
"""


class STTBaseError(Exception):
    """Base exception for all speech-to-text system errors."""

    def __init__(self, message: str, details: dict = None):
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AudioFormatError(STTBaseError):
    """Exception raised for audio format related errors."""

    pass


class ModelLoadError(STTBaseError):
    """Exception raised when model loading fails."""

    pass


class TranscriptionError(STTBaseError):
    """Exception raised when transcription operations fail."""

    pass


class ValidationError(STTBaseError):
    """Exception raised for data validation errors."""

    pass


class ConfigurationError(STTBaseError):
    """Exception raised for configuration related errors."""

    pass
