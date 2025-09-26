"""Audio Format Handler Interface

This module defines the interface for audio format handling operations
including format detection, validation, and conversion utilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import AudioRequest


class AudioFormatHandler(ABC):
    """Abstract base class for audio format handling operations.

    This interface defines the contract for audio format detection,
    validation, and conversion utilities used across the system.
    """

    # Supported audio formats across the system
    SUPPORTED_FORMATS = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]

    def __init__(self):
        """Initialize the audio format handler."""
        pass

    @abstractmethod
    def validate_format(
        self, file_path: str, expected_format: Optional[str] = None
    ) -> bool:
        """Validate that an audio file matches the expected format.

        Args:
            file_path: Path to the audio file
            expected_format: Expected format (if None, validates against supported formats)

        Returns:
            True if format is valid and supported

        Raises:
            AudioFormatError: If format validation fails
            FileNotFoundError: If file doesn't exist
        """
        pass

    @abstractmethod
    def detect_format(self, file_path: str) -> str:
        """Detect the actual format of an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            Detected audio format (e.g., 'wav', 'mp3')

        Raises:
            AudioFormatError: If format cannot be detected
            FileNotFoundError: If file doesn't exist
        """
        pass

    @abstractmethod
    def convert_if_needed(self, file_path: str, target_format: str = "wav") -> str:
        """Convert audio file to target format if needed.

        Args:
            file_path: Path to the source audio file
            target_format: Target format for conversion (default: wav)

        Returns:
            Path to the converted file (or original if no conversion needed)

        Raises:
            AudioFormatError: If conversion fails
            FileNotFoundError: If source file doesn't exist
        """
        pass

    @abstractmethod
    def get_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            Dictionary containing audio metadata:
            - duration: Duration in seconds
            - sample_rate: Sample rate in Hz
            - channels: Number of audio channels
            - bitrate: Bitrate in kbps (if available)
            - format: Detected format
            - size: File size in bytes

        Raises:
            AudioFormatError: If metadata extraction fails
            FileNotFoundError: If file doesn't exist
        """
        pass

    @abstractmethod
    def is_format_supported(self, format_name: str) -> bool:
        """Check if a format is supported by the handler.

        Args:
            format_name: Format name to check (e.g., 'wav', 'mp3')

        Returns:
            True if format is supported
        """
        pass

    def get_supported_formats(self) -> List[str]:
        """Get list of all supported audio formats.

        Returns:
            List of supported format names
        """
        return self.SUPPORTED_FORMATS.copy()

    def validate_audio_request(self, request: AudioRequest) -> None:
        """Validate an audio request for format compatibility.

        Args:
            request: Audio request to validate

        Raises:
            ValidationError: If request validation fails
            AudioFormatError: If audio format is not supported
            FileNotFoundError: If audio file doesn't exist
        """
        # Check if file exists
        import os

        if not os.path.exists(request.file_path):
            from exceptions import ValidationError

            raise ValidationError(f"Audio file not found: {request.file_path}")

        # Validate format is supported
        if not self.is_format_supported(request.audio_format):
            from exceptions import AudioFormatError

            raise AudioFormatError(
                f"Audio format '{request.audio_format}' not supported. "
                f"Supported formats: {self.get_supported_formats()}"
            )

        # Validate actual file format matches declared format
        try:
            detected_format = self.detect_format(request.file_path)
            if detected_format.lower() != request.audio_format.lower():
                from exceptions import AudioFormatError

                raise AudioFormatError(
                    f"File format mismatch. Declared: '{request.audio_format}', "
                    f"Detected: '{detected_format}'"
                )
        except Exception as e:
            from exceptions import ValidationError

            raise ValidationError(f"Failed to validate audio file: {str(e)}")

    def get_conversion_info(
        self, source_format: str, target_format: str
    ) -> Dict[str, Any]:
        """Get information about format conversion requirements.

        Args:
            source_format: Source audio format
            target_format: Target audio format

        Returns:
            Dictionary containing conversion information:
            - needed: Whether conversion is needed
            - supported: Whether conversion is supported
            - quality_loss: Whether conversion may cause quality loss
            - estimated_time: Estimated conversion time factor
        """
        conversion_needed = source_format.lower() != target_format.lower()

        # Quality loss matrix for common conversions
        lossy_formats = {"mp3", "m4a", "ogg"}
        lossless_formats = {"wav", "flac"}

        source_lossy = source_format.lower() in lossy_formats
        target_lossy = target_format.lower() in lossy_formats

        # Quality loss occurs when converting from lossless to lossy,
        # or between different lossy formats
        quality_loss = False
        if conversion_needed:
            if (source_format.lower() in lossless_formats and target_lossy) or (
                source_lossy
                and target_lossy
                and source_format.lower() != target_format.lower()
            ):
                quality_loss = True

        return {
            "needed": conversion_needed,
            "supported": (
                self.is_format_supported(source_format)
                and self.is_format_supported(target_format)
            ),
            "quality_loss": quality_loss,
            "estimated_time": 1.5
            if conversion_needed
            else 0.1,  # Time factor multiplier
        }
