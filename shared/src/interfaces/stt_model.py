"""Speech-to-Text Model Interface

This module defines the abstract interface that all speech-to-text model
implementations must follow. This ensures consistent behavior across
different model types (Whisper, mock, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from stt_shared.models import AudioRequest, ModelConfig, TranscriptionResult


class SpeechToTextModel(ABC):
    """Abstract base class for speech-to-text model implementations.

    This interface defines the contract that all STT model implementations
    must follow, ensuring consistent behavior across different model types.
    """

    def __init__(self, config: ModelConfig):
        """Initialize the model with configuration.

        Args:
            config: Model configuration containing type, path, and parameters
        """
        self.config = config
        self._is_loaded = False

    @abstractmethod
    async def transcribe(self, request: AudioRequest) -> TranscriptionResult:
        """Transcribe audio to text.

        Args:
            request: Audio request containing file path and processing options

        Returns:
            TranscriptionResult containing the transcribed text and metadata

        Raises:
            TranscriptionError: If transcription fails
            AudioFormatError: If audio format is not supported
            ModelLoadError: If model is not properly loaded
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats.

        Returns:
            List of supported audio format extensions (e.g., ['wav', 'mp3'])
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model.

        Returns:
            Dictionary containing model information such as:
            - name: Model name
            - version: Model version
            - type: Model type (whisper, mock, etc.)
            - parameters: Current model parameters
            - loaded: Whether model is loaded
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the model.

        Returns:
            Dictionary containing health status:
            - status: 'healthy', 'degraded', or 'unhealthy'
            - message: Human-readable status message
            - details: Additional diagnostic information
            - timestamp: When the check was performed
        """
        pass

    @abstractmethod
    async def load_model(self) -> None:
        """Load the model into memory.

        This method should be called before transcription operations.
        Implementations should handle model loading, validation, and
        set self._is_loaded = True on success.

        Raises:
            ModelLoadError: If model loading fails
            ConfigurationError: If model configuration is invalid
        """
        pass

    @abstractmethod
    async def unload_model(self) -> None:
        """Unload the model from memory.

        This method should clean up model resources and
        set self._is_loaded = False.
        """
        pass

    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded.

        Returns:
            True if model is loaded and ready for transcription
        """
        return self._is_loaded

    def validate_request(self, request: AudioRequest) -> None:
        """Validate an audio request against model capabilities.

        Args:
            request: Audio request to validate

        Raises:
            ValidationError: If request is invalid
            AudioFormatError: If audio format is not supported
        """
        if not self.is_loaded:
            from ..exceptions import ModelLoadError

            raise ModelLoadError("Model must be loaded before processing requests")

        supported_formats = self.get_supported_formats()
        if request.audio_format.lower() not in supported_formats:
            from ..exceptions import AudioFormatError

            raise AudioFormatError(
                f"Audio format '{request.audio_format}' not supported. "
                f"Supported formats: {supported_formats}"
            )
