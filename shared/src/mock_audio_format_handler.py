"""Mock Audio Format Handler Implementation

This module provides a mock implementation of the AudioFormatHandler interface
for testing purposes. It allows configurable responses, simulated conversions,
and error simulation to facilitate comprehensive testing of audio format handling.
"""

import asyncio
import os
from typing import Any, Dict, Optional

from exceptions import AudioFormatError
from interfaces.audio_format import AudioFormatHandler

from models import AudioRequest


class MockAudioFormatHandler(AudioFormatHandler):
    """Mock implementation of AudioFormatHandler for testing.
    
    This mock handler provides configurable responses, simulated format detection,
    and conversion capabilities for comprehensive testing scenarios.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mock audio format handler.
        
        Args:
            config: Optional configuration dictionary for mock behavior
        """
        super().__init__()

        # Default configuration
        config = config or {}

        # Mock behavior configuration
        self._simulate_file_not_found = config.get("simulate_file_not_found", False)
        self._simulate_format_detection_error = config.get("simulate_format_detection_error", False)
        self._simulate_conversion_error = config.get("simulate_conversion_error", False)
        self._simulate_metadata_error = config.get("simulate_metadata_error", False)
        self._conversion_delay = config.get("conversion_delay", 0.1)  # seconds

        # Mock file format mappings (file_path -> format)
        self._mock_file_formats = config.get("mock_file_formats", {})

        # Mock metadata responses (file_path -> metadata)
        self._mock_metadata = config.get("mock_metadata", {})

        # Mock conversion outputs (source_path -> converted_path)
        self._mock_conversions = config.get("mock_conversions", {})

        # Files that should be treated as existing
        self._mock_existing_files = config.get("mock_existing_files", set())

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
        # Simulate file not found error
        if self._simulate_file_not_found or not self._file_exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Detect the actual format
        try:
            detected_format = self.detect_format(file_path)
        except AudioFormatError:
            return False

        # If no expected format specified, just check if it's supported
        if expected_format is None:
            return self.is_format_supported(detected_format)

        # Check if detected format matches expected format
        return detected_format.lower() == expected_format.lower()

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
        # Simulate file not found error
        if self._simulate_file_not_found or not self._file_exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Simulate format detection error
        if self._simulate_format_detection_error:
            raise AudioFormatError(
                f"Mock format detection error for file: {file_path}",
                details={"simulated": True, "file_path": file_path}
            )

        # Check if we have a mock format mapping for this file
        if file_path in self._mock_file_formats:
            return self._mock_file_formats[file_path]

        # Extract format from file extension as fallback
        _, ext = os.path.splitext(file_path)
        if ext:
            format_name = ext[1:].lower()  # Remove the dot
            if self.is_format_supported(format_name):
                return format_name

        # Default to wav for unknown files
        return "wav"

    async def convert_if_needed(
        self, file_path: str, target_format: str = "wav"
    ) -> str:
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
        # Simulate file not found error
        if self._simulate_file_not_found or not self._file_exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Simulate conversion error
        if self._simulate_conversion_error:
            raise AudioFormatError(
                f"Mock conversion error for file: {file_path}",
                details={
                    "simulated": True,
                    "source_file": file_path,
                    "target_format": target_format
                }
            )

        # Check if target format is supported
        if not self.is_format_supported(target_format):
            raise AudioFormatError(
                f"Target format '{target_format}' not supported. "
                f"Supported formats: {self.get_supported_formats()}"
            )

        # Detect current format
        current_format = self.detect_format(file_path)

        # If already in target format, return original path
        if current_format.lower() == target_format.lower():
            return file_path

        # Simulate conversion delay
        if self._conversion_delay > 0:
            await asyncio.sleep(self._conversion_delay)

        # Check if we have a mock conversion mapping
        conversion_key = f"{file_path}->{target_format}"
        if conversion_key in self._mock_conversions:
            return self._mock_conversions[conversion_key]

        # Generate mock converted file path
        base_path, _ = os.path.splitext(file_path)
        converted_path = f"{base_path}_converted.{target_format}"

        return converted_path

    def get_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary containing audio metadata
            
        Raises:
            AudioFormatError: If metadata extraction fails
            FileNotFoundError: If file doesn't exist
        """
        # Simulate file not found error
        if self._simulate_file_not_found or not self._file_exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Simulate metadata extraction error
        if self._simulate_metadata_error:
            raise AudioFormatError(
                f"Mock metadata extraction error for file: {file_path}",
                details={"simulated": True, "file_path": file_path}
            )

        # Check if we have mock metadata for this file
        if file_path in self._mock_metadata:
            return self._mock_metadata[file_path].copy()

        # Generate default mock metadata
        detected_format = self.detect_format(file_path)

        # Generate realistic mock values based on file path patterns
        duration = self._generate_mock_duration(file_path)
        sample_rate = self._generate_mock_sample_rate(detected_format)
        channels = self._generate_mock_channels(file_path)
        bitrate = self._generate_mock_bitrate(detected_format)
        file_size = self._generate_mock_file_size(duration, bitrate)

        return {
            "duration": duration,
            "sample_rate": sample_rate,
            "channels": channels,
            "bitrate": bitrate,
            "format": detected_format,
            "size": file_size,
            "mock_generated": True,
        }

    def is_format_supported(self, format_name: str) -> bool:
        """Check if a format is supported by the handler.
        
        Args:
            format_name: Format name to check (e.g., 'wav', 'mp3')
            
        Returns:
            True if format is supported
        """
        return format_name.lower() in [fmt.lower() for fmt in self.SUPPORTED_FORMATS]

    def _file_exists(self, file_path: str) -> bool:
        """Check if a file exists (mock implementation).
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file should be treated as existing
        """
        # Check mock existing files set
        if file_path in self._mock_existing_files:
            return True

        # For test files, assume they exist if they have supported extensions
        _, ext = os.path.splitext(file_path)
        if ext and self.is_format_supported(ext[1:]):
            # Treat test files as existing
            if "/test/" in file_path or file_path.startswith("test_"):
                return True

        # Fall back to actual file system check
        return os.path.exists(file_path)

    def _generate_mock_duration(self, file_path: str) -> float:
        """Generate mock duration based on file path patterns."""
        filename = os.path.basename(file_path).lower()

        if "short" in filename:
            return 5.2
        elif "long" in filename or "extended" in filename:
            return 180.7
        elif "empty" in filename or "silent" in filename:
            return 0.0
        else:
            return 30.5  # Default duration

    def _generate_mock_sample_rate(self, format_name: str) -> int:
        """Generate mock sample rate based on format."""
        format_rates = {
            "wav": 44100,
            "flac": 48000,
            "mp3": 44100,
            "m4a": 44100,
            "mp4": 44100,
            "ogg": 44100,
        }
        return format_rates.get(format_name.lower(), 44100)

    def _generate_mock_channels(self, file_path: str) -> int:
        """Generate mock channel count based on file path patterns."""
        filename = os.path.basename(file_path).lower()

        if "mono" in filename:
            return 1
        elif "stereo" in filename or "2ch" in filename:
            return 2
        elif "surround" in filename or "5.1" in filename:
            return 6
        else:
            return 2  # Default to stereo

    def _generate_mock_bitrate(self, format_name: str) -> Optional[int]:
        """Generate mock bitrate based on format."""
        format_bitrates = {
            "mp3": 320,
            "m4a": 256,
            "mp4": 256,
            "ogg": 320,
            "wav": None,  # Uncompressed
            "flac": None,  # Lossless
        }
        return format_bitrates.get(format_name.lower())

    def _generate_mock_file_size(self, duration: float, bitrate: Optional[int]) -> int:
        """Generate mock file size based on duration and bitrate."""
        if bitrate is None:
            # Uncompressed audio (roughly 1.4 MB per minute for stereo 44.1kHz 16-bit)
            return int(duration * 1.4 * 1024 * 1024 / 60)
        else:
            # Compressed audio
            return int(duration * bitrate * 1024 / 8)

    def configure_mock_behavior(self, **kwargs) -> None:
        """Configure mock behavior at runtime.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        if "simulate_file_not_found" in kwargs:
            self._simulate_file_not_found = kwargs["simulate_file_not_found"]
        if "simulate_format_detection_error" in kwargs:
            self._simulate_format_detection_error = kwargs["simulate_format_detection_error"]
        if "simulate_conversion_error" in kwargs:
            self._simulate_conversion_error = kwargs["simulate_conversion_error"]
        if "simulate_metadata_error" in kwargs:
            self._simulate_metadata_error = kwargs["simulate_metadata_error"]
        if "conversion_delay" in kwargs:
            self._conversion_delay = kwargs["conversion_delay"]

    def add_mock_file(self, file_path: str, format_name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a mock file for testing.
        
        Args:
            file_path: Path to the mock file
            format_name: Format of the mock file
            metadata: Optional metadata for the mock file
        """
        self._mock_existing_files.add(file_path)
        self._mock_file_formats[file_path] = format_name
        if metadata:
            self._mock_metadata[file_path] = metadata

    def add_mock_conversion(self, source_path: str, target_format: str, converted_path: str) -> None:
        """Add a mock conversion mapping.
        
        Args:
            source_path: Source file path
            target_format: Target format
            converted_path: Path to converted file
        """
        conversion_key = f"{source_path}->{target_format}"
        self._mock_conversions[conversion_key] = converted_path

    def validate_audio_request(self, request: AudioRequest) -> None:
        """Validate an audio request for format compatibility (mock implementation).
        
        Args:
            request: Audio request to validate
            
        Raises:
            ValidationError: If request validation fails
            AudioFormatError: If audio format is not supported
            FileNotFoundError: If audio file doesn't exist
        """
        # Check if file exists using mock implementation
        if not self._file_exists(request.file_path):
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

    def reset_mock_state(self) -> None:
        """Reset all mock state to defaults."""
        self._simulate_file_not_found = False
        self._simulate_format_detection_error = False
        self._simulate_conversion_error = False
        self._simulate_metadata_error = False
        self._conversion_delay = 0.1
        self._mock_file_formats.clear()
        self._mock_metadata.clear()
        self._mock_conversions.clear()
        self._mock_existing_files.clear()
