"""Interface contract tests for AudioFormatHandler implementations.

These tests verify that any implementation of the AudioFormatHandler interface
follows the expected contract and behavior.
"""

import os
import tempfile
from abc import ABC

import pytest
from interfaces.audio_format import AudioFormatHandler

from models import AudioRequest


class MockAudioFormatHandler(AudioFormatHandler):
    """Mock implementation for testing the interface contract."""

    def __init__(self):
        super().__init__()
        self._mock_files = {}  # file_path -> format mapping

    def add_mock_file(self, file_path: str, format_name: str):
        """Add a mock file for testing."""
        self._mock_files[file_path] = format_name

    def validate_format(self, file_path: str, expected_format: str = None) -> bool:
        """Mock format validation."""
        if file_path not in self._mock_files:
            raise FileNotFoundError(f"File not found: {file_path}")

        detected = self._mock_files[file_path]

        if expected_format:
            return detected.lower() == expected_format.lower()

        return detected.lower() in [fmt.lower() for fmt in self.SUPPORTED_FORMATS]

    def detect_format(self, file_path: str) -> str:
        """Mock format detection."""
        if file_path not in self._mock_files:
            raise FileNotFoundError(f"File not found: {file_path}")

        return self._mock_files[file_path]

    async def convert_if_needed(
        self, file_path: str, target_format: str = "wav"
    ) -> str:
        """Mock conversion."""
        if file_path not in self._mock_files:
            raise FileNotFoundError(f"File not found: {file_path}")

        current_format = self._mock_files[file_path]

        if current_format.lower() == target_format.lower():
            return file_path  # No conversion needed

        # Mock conversion by creating new path
        base, ext = os.path.splitext(file_path)
        converted_path = f"{base}_converted.{target_format}"
        self._mock_files[converted_path] = target_format

        return converted_path

    def get_audio_metadata(self, file_path: str) -> dict:
        """Mock metadata extraction."""
        if file_path not in self._mock_files:
            raise FileNotFoundError(f"File not found: {file_path}")

        format_name = self._mock_files[file_path]

        return {
            "duration": 10.5,
            "sample_rate": 44100,
            "channels": 2,
            "bitrate": 320 if format_name == "mp3" else None,
            "format": format_name,
            "size": 1024000,
        }

    def is_format_supported(self, format_name: str) -> bool:
        """Mock format support check."""
        return format_name.lower() in [fmt.lower() for fmt in self.SUPPORTED_FORMATS]


class TestAudioFormatHandlerInterface:
    """Test cases for the AudioFormatHandler interface contract."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MockAudioFormatHandler()
        self.test_file = "/test/audio.wav"
        self.handler.add_mock_file(self.test_file, "wav")

    def test_interface_is_abstract(self):
        """Test that AudioFormatHandler is an abstract base class."""
        assert issubclass(AudioFormatHandler, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            AudioFormatHandler()

    def test_supported_formats_constant(self):
        """Test that SUPPORTED_FORMATS constant is defined."""
        assert hasattr(AudioFormatHandler, "SUPPORTED_FORMATS")
        assert isinstance(AudioFormatHandler.SUPPORTED_FORMATS, list)
        assert len(AudioFormatHandler.SUPPORTED_FORMATS) > 0

        expected_formats = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]
        assert AudioFormatHandler.SUPPORTED_FORMATS == expected_formats

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.handler.get_supported_formats()
        assert isinstance(formats, list)
        assert formats == AudioFormatHandler.SUPPORTED_FORMATS

        # Should return a copy, not the original
        formats.append("test")
        assert "test" not in self.handler.get_supported_formats()

    def test_validate_format(self):
        """Test format validation."""
        # Valid format
        assert self.handler.validate_format(self.test_file, "wav") is True

        # Invalid format
        assert self.handler.validate_format(self.test_file, "mp3") is False

        # No expected format (should validate against supported formats)
        assert self.handler.validate_format(self.test_file) is True

        # File not found
        with pytest.raises(FileNotFoundError):
            self.handler.validate_format("/nonexistent/file.wav")

    def test_detect_format(self):
        """Test format detection."""
        format_detected = self.handler.detect_format(self.test_file)
        assert format_detected == "wav"

        # File not found
        with pytest.raises(FileNotFoundError):
            self.handler.detect_format("/nonexistent/file.wav")

    @pytest.mark.asyncio
    async def test_convert_if_needed(self):
        """Test audio conversion."""
        # No conversion needed (same format)
        result = await self.handler.convert_if_needed(self.test_file, "wav")
        assert result == self.test_file

        # Conversion needed
        result = await self.handler.convert_if_needed(self.test_file, "mp3")
        assert result != self.test_file
        assert result.endswith("_converted.mp3")

        # File not found
        with pytest.raises(FileNotFoundError):
            await self.handler.convert_if_needed("/nonexistent/file.wav")

    def test_get_audio_metadata(self):
        """Test metadata extraction."""
        metadata = self.handler.get_audio_metadata(self.test_file)
        assert isinstance(metadata, dict)

        # Check required fields
        required_fields = ["duration", "sample_rate", "channels", "format", "size"]
        for field in required_fields:
            assert field in metadata

        assert isinstance(metadata["duration"], (int, float))
        assert isinstance(metadata["sample_rate"], int)
        assert isinstance(metadata["channels"], int)
        assert isinstance(metadata["format"], str)
        assert isinstance(metadata["size"], int)

        # File not found
        with pytest.raises(FileNotFoundError):
            self.handler.get_audio_metadata("/nonexistent/file.wav")

    def test_is_format_supported(self):
        """Test format support checking."""
        # Supported formats
        for fmt in AudioFormatHandler.SUPPORTED_FORMATS:
            assert self.handler.is_format_supported(fmt) is True
            assert self.handler.is_format_supported(fmt.upper()) is True

        # Unsupported format
        assert self.handler.is_format_supported("xyz") is False
        assert self.handler.is_format_supported("unknown") is False

    def test_get_conversion_info(self):
        """Test conversion information."""
        # No conversion needed
        info = self.handler.get_conversion_info("wav", "wav")
        assert info["needed"] is False
        assert info["supported"] is True
        assert info["quality_loss"] is False
        assert info["estimated_time"] == 0.1

        # Conversion needed (lossless to lossy)
        info = self.handler.get_conversion_info("wav", "mp3")
        assert info["needed"] is True
        assert info["supported"] is True
        assert info["quality_loss"] is True
        assert info["estimated_time"] == 1.5

        # Conversion needed (lossy to lossless)
        info = self.handler.get_conversion_info("mp3", "wav")
        assert info["needed"] is True
        assert info["supported"] is True
        assert info["quality_loss"] is False  # No additional loss

        # Between lossy formats
        info = self.handler.get_conversion_info("mp3", "ogg")
        assert info["needed"] is True
        assert info["quality_loss"] is True


class TestAudioRequestValidation:
    """Test audio request validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MockAudioFormatHandler()

        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        self.temp_file.close()
        self.temp_path = self.temp_file.name

        # Add to mock handler
        self.handler.add_mock_file(self.temp_path, "wav")

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)

    def test_validate_audio_request_success(self):
        """Test successful audio request validation."""
        request = AudioRequest(file_path=self.temp_path, audio_format="wav")

        # Should not raise any exception
        self.handler.validate_audio_request(request)

    def test_validate_audio_request_file_not_found(self):
        """Test validation with non-existent file."""
        request = AudioRequest(file_path="/nonexistent/file.wav", audio_format="wav")

        with pytest.raises(Exception):  # ValidationError when exceptions module exists
            self.handler.validate_audio_request(request)

    def test_validate_audio_request_unsupported_format(self):
        """Test validation with unsupported format."""
        # Create request with supported format first, then modify it
        request = AudioRequest(file_path=self.temp_path, audio_format="wav")

        # Manually set unsupported format to bypass AudioRequest validation
        request.audio_format = "xyz"

        with pytest.raises(Exception):  # AudioFormatError when exceptions module exists
            self.handler.validate_audio_request(request)


class TestInterfaceContractCompliance:
    """Test that implementations must follow the interface contract."""

    def test_incomplete_implementation_fails(self):
        """Test that incomplete implementations cannot be instantiated."""

        class IncompleteHandler(AudioFormatHandler):
            """Incomplete implementation missing required methods."""

            pass

        # Should fail to instantiate due to missing abstract methods
        with pytest.raises(TypeError):
            IncompleteHandler()

    def test_all_abstract_methods_must_be_implemented(self):
        """Test that all abstract methods must be implemented."""

        # Get all abstract methods from the interface
        abstract_methods = {
            name
            for name, method in AudioFormatHandler.__dict__.items()
            if getattr(method, "__isabstractmethod__", False)
        }

        expected_methods = {
            "validate_format",
            "detect_format",
            "convert_if_needed",
            "get_audio_metadata",
            "is_format_supported",
        }

        assert abstract_methods == expected_methods
