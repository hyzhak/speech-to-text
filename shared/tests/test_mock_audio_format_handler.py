"""Tests for MockAudioFormatHandler

This module contains comprehensive unit tests for the MockAudioFormatHandler
implementation, covering all functionality including configurable responses,
error simulation, and interface contract compliance.
"""

import asyncio

import pytest
from exceptions import AudioFormatError, ValidationError
from interfaces.audio_format import AudioFormatHandler
from mock_audio_format_handler import MockAudioFormatHandler

from models import AudioRequest


class TestMockAudioFormatHandler:
    """Test suite for MockAudioFormatHandler."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.handler = MockAudioFormatHandler()

    def test_handler_initialization(self):
        """Test that the mock handler initializes correctly."""
        assert isinstance(self.handler, AudioFormatHandler)
        assert not self.handler._simulate_file_not_found
        assert not self.handler._simulate_format_detection_error
        assert not self.handler._simulate_conversion_error
        assert not self.handler._simulate_metadata_error
        assert self.handler._conversion_delay == 0.1

    def test_handler_initialization_with_config(self):
        """Test handler initialization with custom configuration."""
        config = {
            "simulate_file_not_found": True,
            "simulate_format_detection_error": True,
            "conversion_delay": 0.5,
            "mock_file_formats": {"/test/audio.wav": "wav"},
            "mock_existing_files": {"/test/audio.wav"}
        }

        handler = MockAudioFormatHandler(config)

        assert handler._simulate_file_not_found is True
        assert handler._simulate_format_detection_error is True
        assert handler._conversion_delay == 0.5
        assert "/test/audio.wav" in handler._mock_file_formats
        assert "/test/audio.wav" in handler._mock_existing_files

    def test_get_supported_formats(self):
        """Test that supported formats are returned correctly."""
        formats = self.handler.get_supported_formats()

        expected_formats = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]
        assert formats == expected_formats

        # Ensure it returns a copy (not the original list)
        formats.append("test")
        assert self.handler.get_supported_formats() == expected_formats

    def test_is_format_supported(self):
        """Test format support checking."""
        # Test supported formats
        assert self.handler.is_format_supported("wav") is True
        assert self.handler.is_format_supported("mp3") is True
        assert self.handler.is_format_supported("WAV") is True  # Case insensitive

        # Test unsupported formats
        assert self.handler.is_format_supported("xyz") is False
        assert self.handler.is_format_supported("") is False

    def test_detect_format_from_extension(self):
        """Test format detection from file extension."""
        # Add mock files
        self.handler.add_mock_file("/test/audio.wav", "wav")
        self.handler.add_mock_file("/test/music.mp3", "mp3")

        assert self.handler.detect_format("/test/audio.wav") == "wav"
        assert self.handler.detect_format("/test/music.mp3") == "mp3"

    def test_detect_format_from_mock_mapping(self):
        """Test format detection using mock format mappings."""
        # Add a file with format different from extension
        self.handler.add_mock_file("/test/audio.xyz", "wav")

        assert self.handler.detect_format("/test/audio.xyz") == "wav"

    def test_detect_format_file_not_found(self):
        """Test format detection when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            self.handler.detect_format("/nonexistent/file.wav")

    def test_detect_format_error_simulation(self):
        """Test format detection error simulation."""
        self.handler.add_mock_file("/test/audio.wav", "wav")
        self.handler.configure_mock_behavior(simulate_format_detection_error=True)

        with pytest.raises(AudioFormatError) as exc_info:
            self.handler.detect_format("/test/audio.wav")

        assert "Mock format detection error" in str(exc_info.value)
        assert exc_info.value.details["simulated"] is True

    def test_validate_format_success(self):
        """Test successful format validation."""
        self.handler.add_mock_file("/test/audio.wav", "wav")

        # Validate without expected format
        assert self.handler.validate_format("/test/audio.wav") is True

        # Validate with matching expected format
        assert self.handler.validate_format("/test/audio.wav", "wav") is True

    def test_validate_format_mismatch(self):
        """Test format validation with format mismatch."""
        self.handler.add_mock_file("/test/audio.wav", "wav")

        # Expected format doesn't match detected format
        assert self.handler.validate_format("/test/audio.wav", "mp3") is False

    def test_validate_format_file_not_found(self):
        """Test format validation when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            self.handler.validate_format("/nonexistent/file.wav")

    def test_validate_format_unsupported(self):
        """Test format validation with unsupported format."""
        self.handler.add_mock_file("/test/audio.xyz", "xyz")

        # Should return False for unsupported format
        assert self.handler.validate_format("/test/audio.xyz") is False

    @pytest.mark.asyncio
    async def test_convert_if_needed_no_conversion(self):
        """Test conversion when no conversion is needed."""
        self.handler.add_mock_file("/test/audio.wav", "wav")

        result = await self.handler.convert_if_needed("/test/audio.wav", "wav")

        # Should return original path when no conversion needed
        assert result == "/test/audio.wav"

    @pytest.mark.asyncio
    async def test_convert_if_needed_with_conversion(self):
        """Test conversion when conversion is needed."""
        self.handler.add_mock_file("/test/audio.mp3", "mp3")

        result = await self.handler.convert_if_needed("/test/audio.mp3", "wav")

        # Should return converted path
        assert result == "/test/audio_converted.wav"
        assert result != "/test/audio.mp3"

    @pytest.mark.asyncio
    async def test_convert_if_needed_with_mock_mapping(self):
        """Test conversion using mock conversion mappings."""
        self.handler.add_mock_file("/test/audio.mp3", "mp3")
        self.handler.add_mock_conversion("/test/audio.mp3", "wav", "/test/converted_audio.wav")

        result = await self.handler.convert_if_needed("/test/audio.mp3", "wav")

        assert result == "/test/converted_audio.wav"

    @pytest.mark.asyncio
    async def test_convert_if_needed_file_not_found(self):
        """Test conversion when source file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            await self.handler.convert_if_needed("/nonexistent/file.wav", "mp3")

    @pytest.mark.asyncio
    async def test_convert_if_needed_unsupported_target(self):
        """Test conversion to unsupported target format."""
        self.handler.add_mock_file("/test/audio.wav", "wav")

        with pytest.raises(AudioFormatError) as exc_info:
            await self.handler.convert_if_needed("/test/audio.wav", "xyz")

        assert "Target format 'xyz' not supported" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_convert_if_needed_error_simulation(self):
        """Test conversion error simulation."""
        self.handler.add_mock_file("/test/audio.wav", "wav")
        self.handler.configure_mock_behavior(simulate_conversion_error=True)

        with pytest.raises(AudioFormatError) as exc_info:
            await self.handler.convert_if_needed("/test/audio.wav", "mp3")

        assert "Mock conversion error" in str(exc_info.value)
        assert exc_info.value.details["simulated"] is True

    @pytest.mark.asyncio
    async def test_convert_if_needed_timing(self):
        """Test that conversion delay is applied."""
        self.handler.add_mock_file("/test/audio.mp3", "mp3")
        self.handler.configure_mock_behavior(conversion_delay=0.1)

        start_time = asyncio.get_event_loop().time()
        await self.handler.convert_if_needed("/test/audio.mp3", "wav")
        end_time = asyncio.get_event_loop().time()

        # Should take at least the conversion delay time
        assert (end_time - start_time) >= 0.1

    def test_get_audio_metadata_default(self):
        """Test getting default mock metadata."""
        self.handler.add_mock_file("/test/audio.wav", "wav")

        metadata = self.handler.get_audio_metadata("/test/audio.wav")

        assert "duration" in metadata
        assert "sample_rate" in metadata
        assert "channels" in metadata
        assert "format" in metadata
        assert "size" in metadata
        assert metadata["format"] == "wav"
        assert metadata["mock_generated"] is True

    def test_get_audio_metadata_custom(self):
        """Test getting custom mock metadata."""
        custom_metadata = {
            "duration": 120.5,
            "sample_rate": 48000,
            "channels": 2,
            "bitrate": 320,
            "format": "mp3",
            "size": 4800000
        }

        self.handler.add_mock_file("/test/music.mp3", "mp3", custom_metadata)

        metadata = self.handler.get_audio_metadata("/test/music.mp3")

        assert metadata["duration"] == 120.5
        assert metadata["sample_rate"] == 48000
        assert metadata["channels"] == 2
        assert metadata["bitrate"] == 320
        assert metadata["format"] == "mp3"
        assert metadata["size"] == 4800000

    def test_get_audio_metadata_pattern_based(self):
        """Test metadata generation based on file path patterns."""
        # Test short file
        self.handler.add_mock_file("/test/short_audio.wav", "wav")
        metadata_short = self.handler.get_audio_metadata("/test/short_audio.wav")
        assert metadata_short["duration"] == 5.2

        # Test long file
        self.handler.add_mock_file("/test/long_audio.wav", "wav")
        metadata_long = self.handler.get_audio_metadata("/test/long_audio.wav")
        assert metadata_long["duration"] == 180.7

        # Test mono file
        self.handler.add_mock_file("/test/mono_audio.wav", "wav")
        metadata_mono = self.handler.get_audio_metadata("/test/mono_audio.wav")
        assert metadata_mono["channels"] == 1

    def test_get_audio_metadata_file_not_found(self):
        """Test metadata extraction when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            self.handler.get_audio_metadata("/nonexistent/file.wav")

    def test_get_audio_metadata_error_simulation(self):
        """Test metadata extraction error simulation."""
        self.handler.add_mock_file("/test/audio.wav", "wav")
        self.handler.configure_mock_behavior(simulate_metadata_error=True)

        with pytest.raises(AudioFormatError) as exc_info:
            self.handler.get_audio_metadata("/test/audio.wav")

        assert "Mock metadata extraction error" in str(exc_info.value)
        assert exc_info.value.details["simulated"] is True

    def test_validate_audio_request_success(self):
        """Test successful audio request validation."""
        self.handler.add_mock_file("/test/audio.wav", "wav")

        request = AudioRequest(
            file_path="/test/audio.wav",
            audio_format="wav"
        )

        # Should not raise any exception
        self.handler.validate_audio_request(request)

    def test_validate_audio_request_file_not_found(self):
        """Test audio request validation when file doesn't exist."""
        request = AudioRequest(
            file_path="/nonexistent/file.wav",
            audio_format="wav"
        )

        with pytest.raises(ValidationError) as exc_info:
            self.handler.validate_audio_request(request)

        assert "Audio file not found" in str(exc_info.value)

    def test_validate_audio_request_unsupported_format(self):
        """Test audio request validation with unsupported format."""
        # The AudioRequest validation will catch this before it gets to the handler
        with pytest.raises(ValueError) as exc_info:
            AudioRequest(
                file_path="/test/audio.xyz",
                audio_format="xyz"
            )

        assert "Unsupported audio format: xyz" in str(exc_info.value)

    def test_validate_audio_request_format_mismatch(self):
        """Test audio request validation with format mismatch."""
        self.handler.add_mock_file("/test/audio.wav", "wav")

        request = AudioRequest(
            file_path="/test/audio.wav",
            audio_format="mp3"  # Declared as mp3 but actually wav
        )

        with pytest.raises(ValidationError) as exc_info:
            self.handler.validate_audio_request(request)

        assert "File format mismatch" in str(exc_info.value)

    def test_get_conversion_info(self):
        """Test getting conversion information."""
        # No conversion needed
        info = self.handler.get_conversion_info("wav", "wav")
        assert info["needed"] is False
        assert info["supported"] is True
        assert info["quality_loss"] is False

        # Conversion needed, no quality loss
        info = self.handler.get_conversion_info("wav", "flac")
        assert info["needed"] is True
        assert info["supported"] is True
        assert info["quality_loss"] is False

        # Conversion with quality loss
        info = self.handler.get_conversion_info("wav", "mp3")
        assert info["needed"] is True
        assert info["supported"] is True
        assert info["quality_loss"] is True

    def test_configure_mock_behavior(self):
        """Test runtime configuration of mock behavior."""
        # Test file not found simulation
        self.handler.configure_mock_behavior(simulate_file_not_found=True)
        assert self.handler._simulate_file_not_found is True

        # Test format detection error simulation
        self.handler.configure_mock_behavior(simulate_format_detection_error=True)
        assert self.handler._simulate_format_detection_error is True

        # Test conversion delay configuration
        self.handler.configure_mock_behavior(conversion_delay=0.5)
        assert self.handler._conversion_delay == 0.5

    def test_add_mock_file(self):
        """Test adding mock files."""
        metadata = {"duration": 60.0, "sample_rate": 44100}

        self.handler.add_mock_file("/test/custom.wav", "wav", metadata)

        assert "/test/custom.wav" in self.handler._mock_existing_files
        assert self.handler._mock_file_formats["/test/custom.wav"] == "wav"
        assert self.handler._mock_metadata["/test/custom.wav"] == metadata

    def test_add_mock_conversion(self):
        """Test adding mock conversion mappings."""
        self.handler.add_mock_conversion("/test/source.mp3", "wav", "/test/converted.wav")

        conversion_key = "/test/source.mp3->wav"
        assert self.handler._mock_conversions[conversion_key] == "/test/converted.wav"

    def test_reset_mock_state(self):
        """Test resetting mock state."""
        # Configure some mock state
        self.handler.configure_mock_behavior(
            simulate_file_not_found=True,
            conversion_delay=1.0
        )
        self.handler.add_mock_file("/test/audio.wav", "wav")
        self.handler.add_mock_conversion("/test/source.mp3", "wav", "/test/converted.wav")

        # Reset state
        self.handler.reset_mock_state()

        # Verify everything is reset
        assert self.handler._simulate_file_not_found is False
        assert self.handler._conversion_delay == 0.1
        assert len(self.handler._mock_file_formats) == 0
        assert len(self.handler._mock_conversions) == 0
        assert len(self.handler._mock_existing_files) == 0

    def test_file_exists_mock_files(self):
        """Test file existence checking with mock files."""
        # File not in mock set
        assert self.handler._file_exists("/nonexistent/file.wav") is False

        # Add to mock existing files
        self.handler.add_mock_file("/test/audio.wav", "wav")
        assert self.handler._file_exists("/test/audio.wav") is True

    def test_file_exists_test_files(self):
        """Test file existence checking for test files."""
        # Test files with supported extensions should be treated as existing
        assert self.handler._file_exists("/test/audio.wav") is True
        assert self.handler._file_exists("test_audio.mp3") is True

        # Non-test files with unsupported extensions should not
        assert self.handler._file_exists("/regular/audio.xyz") is False

    def test_interface_contract_compliance(self):
        """Test that MockAudioFormatHandler properly implements the interface."""
        assert isinstance(self.handler, AudioFormatHandler)

        # Check that all abstract methods are implemented
        abstract_methods = [
            'validate_format', 'detect_format', 'convert_if_needed',
            'get_audio_metadata', 'is_format_supported'
        ]

        for method_name in abstract_methods:
            assert hasattr(self.handler, method_name)
            assert callable(getattr(self.handler, method_name))

    def test_mock_duration_generation(self):
        """Test mock duration generation patterns."""
        assert self.handler._generate_mock_duration("/test/short_audio.wav") == 5.2
        assert self.handler._generate_mock_duration("/test/long_audio.wav") == 180.7
        assert self.handler._generate_mock_duration("/test/empty_audio.wav") == 0.0
        assert self.handler._generate_mock_duration("/test/normal_audio.wav") == 30.5

    def test_mock_sample_rate_generation(self):
        """Test mock sample rate generation by format."""
        assert self.handler._generate_mock_sample_rate("wav") == 44100
        assert self.handler._generate_mock_sample_rate("flac") == 48000
        assert self.handler._generate_mock_sample_rate("mp3") == 44100
        assert self.handler._generate_mock_sample_rate("unknown") == 44100

    def test_mock_channels_generation(self):
        """Test mock channel count generation patterns."""
        assert self.handler._generate_mock_channels("/test/mono_audio.wav") == 1
        assert self.handler._generate_mock_channels("/test/stereo_audio.wav") == 2
        assert self.handler._generate_mock_channels("/test/surround_audio.wav") == 6
        assert self.handler._generate_mock_channels("/test/normal_audio.wav") == 2

    def test_mock_bitrate_generation(self):
        """Test mock bitrate generation by format."""
        assert self.handler._generate_mock_bitrate("mp3") == 320
        assert self.handler._generate_mock_bitrate("m4a") == 256
        assert self.handler._generate_mock_bitrate("wav") is None
        assert self.handler._generate_mock_bitrate("flac") is None

    def test_mock_file_size_generation(self):
        """Test mock file size generation."""
        # Compressed format
        size_compressed = self.handler._generate_mock_file_size(60.0, 320)
        assert size_compressed > 0

        # Uncompressed format
        size_uncompressed = self.handler._generate_mock_file_size(60.0, None)
        assert size_uncompressed > 0

        # For short durations, compressed might be larger due to overhead
        # Test with longer duration where uncompressed should be larger
        size_compressed_long = self.handler._generate_mock_file_size(300.0, 128)  # Lower bitrate
        size_uncompressed_long = self.handler._generate_mock_file_size(300.0, None)
        assert size_uncompressed_long > size_compressed_long


# Integration tests for error simulation behavior
class TestMockAudioFormatHandlerErrorSimulation:
    """Test suite for error simulation behavior."""

    def test_file_not_found_simulation_consistency(self):
        """Test that file not found simulation affects all methods consistently."""
        handler = MockAudioFormatHandler()
        handler.configure_mock_behavior(simulate_file_not_found=True)

        # All methods should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            handler.detect_format("/test/audio.wav")

        with pytest.raises(FileNotFoundError):
            handler.validate_format("/test/audio.wav")

        with pytest.raises(FileNotFoundError):
            handler.get_audio_metadata("/test/audio.wav")

    @pytest.mark.asyncio
    async def test_conversion_error_simulation_with_valid_file(self):
        """Test conversion error simulation with otherwise valid file."""
        handler = MockAudioFormatHandler()
        handler.add_mock_file("/test/audio.wav", "wav")
        handler.configure_mock_behavior(simulate_conversion_error=True)

        # Should raise conversion error even though file exists and format is valid
        with pytest.raises(AudioFormatError) as exc_info:
            await handler.convert_if_needed("/test/audio.wav", "mp3")

        assert exc_info.value.details["simulated"] is True
        assert exc_info.value.details["source_file"] == "/test/audio.wav"
        assert exc_info.value.details["target_format"] == "mp3"


if __name__ == "__main__":
    pytest.main([__file__])
