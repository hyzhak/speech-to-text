"""Unit tests for shared data models."""

import os
import sys
from datetime import datetime

import pytest

# Add the src directory to the path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models import AudioRequest, ModelConfig, STTError, TranscriptionResult


class TestAudioRequest:
    """Test cases for AudioRequest data model."""

    def test_valid_audio_request(self):
        """Test creating a valid AudioRequest."""
        request = AudioRequest(
            file_path="/path/to/audio.wav", audio_format="wav", output_format="text"
        )
        assert request.file_path == "/path/to/audio.wav"
        assert request.audio_format == "wav"
        assert request.output_format == "text"
        assert request.model_config == {}
        assert request.metadata == {}

    def test_audio_request_with_optional_fields(self):
        """Test AudioRequest with optional fields."""
        config = {"model_size": "base"}
        metadata = {"source": "test"}

        request = AudioRequest(
            file_path="/path/to/audio.mp3",
            audio_format="mp3",
            output_format="json",
            model_config=config,
            metadata=metadata,
        )

        assert request.model_config == config
        assert request.metadata == metadata
        assert request.output_format == "json"

    def test_empty_file_path_raises_error(self):
        """Test that empty file_path raises ValueError."""
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            AudioRequest(file_path="", audio_format="wav")

    def test_unsupported_audio_format_raises_error(self):
        """Test that unsupported audio format raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported audio format: xyz"):
            AudioRequest(file_path="/path/to/audio.xyz", audio_format="xyz")

    def test_unsupported_output_format_raises_error(self):
        """Test that unsupported output format raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported output format: xml"):
            AudioRequest(
                file_path="/path/to/audio.wav", audio_format="wav", output_format="xml"
            )

    def test_supported_audio_formats(self):
        """Test all supported audio formats are accepted."""
        supported_formats = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]

        for fmt in supported_formats:
            request = AudioRequest(file_path=f"/path/to/audio.{fmt}", audio_format=fmt)
            assert request.audio_format == fmt


class TestTranscriptionResult:
    """Test cases for TranscriptionResult data model."""

    def test_valid_transcription_result(self):
        """Test creating a valid TranscriptionResult."""
        result = TranscriptionResult(
            text="Hello world",
            confidence=0.95,
            processing_time=2.5,
            model_used="whisper-base",
        )

        assert result.text == "Hello world"
        assert result.confidence == 0.95
        assert result.processing_time == 2.5
        assert result.model_used == "whisper-base"
        assert result.metadata == {}
        assert isinstance(result.timestamp, datetime)

    def test_transcription_result_with_metadata(self):
        """Test TranscriptionResult with metadata."""
        metadata = {"language": "en", "segments": 5}

        result = TranscriptionResult(
            text="Test transcription",
            confidence=0.88,
            processing_time=1.2,
            model_used="whisper-small",
            metadata=metadata,
        )

        assert result.metadata == metadata

    def test_confidence_validation(self):
        """Test confidence value validation."""
        # Test valid confidence values
        for confidence in [0.0, 0.5, 1.0]:
            result = TranscriptionResult(
                text="test",
                confidence=confidence,
                processing_time=1.0,
                model_used="test-model",
            )
            assert result.confidence == confidence

        # Test invalid confidence values
        invalid_values = [-0.1, 1.1, 2.0, "0.5", None]
        for invalid_confidence in invalid_values:
            with pytest.raises(
                ValueError, match="confidence must be a number between 0.0 and 1.0"
            ):
                TranscriptionResult(
                    text="test",
                    confidence=invalid_confidence,
                    processing_time=1.0,
                    model_used="test-model",
                )

    def test_processing_time_validation(self):
        """Test processing_time value validation."""
        # Test valid processing times
        for time_val in [0.0, 1.5, 100.0]:
            result = TranscriptionResult(
                text="test",
                confidence=0.9,
                processing_time=time_val,
                model_used="test-model",
            )
            assert result.processing_time == time_val

        # Test invalid processing times
        invalid_values = [-1.0, -0.1, "1.5", None]
        for invalid_time in invalid_values:
            with pytest.raises(
                ValueError, match="processing_time must be a non-negative number"
            ):
                TranscriptionResult(
                    text="test",
                    confidence=0.9,
                    processing_time=invalid_time,
                    model_used="test-model",
                )

    def test_empty_model_used_raises_error(self):
        """Test that empty model_used raises ValueError."""
        with pytest.raises(ValueError, match="model_used cannot be empty"):
            TranscriptionResult(
                text="test", confidence=0.9, processing_time=1.0, model_used=""
            )


class TestModelConfig:
    """Test cases for ModelConfig data model."""

    def test_valid_model_config(self):
        """Test creating a valid ModelConfig."""
        config = ModelConfig(model_type="whisper", model_path="/path/to/model")

        assert config.model_type == "whisper"
        assert config.model_path == "/path/to/model"
        assert config.parameters == {}
        assert config.fallback_enabled is True

    def test_model_config_with_parameters(self):
        """Test ModelConfig with parameters."""
        parameters = {"size": "base", "language": "en"}

        config = ModelConfig(
            model_type="whisper",
            model_path="/path/to/model",
            parameters=parameters,
            fallback_enabled=False,
        )

        assert config.parameters == parameters
        assert config.fallback_enabled is False

    def test_supported_model_types(self):
        """Test all supported model types are accepted."""
        supported_types = ["whisper", "mock"]

        for model_type in supported_types:
            config = ModelConfig(model_type=model_type, model_path="/path/to/model")
            assert config.model_type == model_type

    def test_unsupported_model_type_raises_error(self):
        """Test that unsupported model type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported model type: unknown"):
            ModelConfig(model_type="unknown", model_path="/path/to/model")

    def test_empty_model_path_raises_error(self):
        """Test that empty model_path raises ValueError."""
        with pytest.raises(ValueError, match="model_path cannot be empty"):
            ModelConfig(model_type="whisper", model_path="")


class TestSTTError:
    """Test cases for STTError data model."""

    def test_valid_stt_error(self):
        """Test creating a valid STTError."""
        error = STTError(message="Test error message", error_code="TEST_ERROR")

        assert error.message == "Test error message"
        assert error.error_code == "TEST_ERROR"
        assert error.details == {}
        assert isinstance(error.timestamp, datetime)

    def test_stt_error_with_details(self):
        """Test STTError with details."""
        details = {"file_path": "/test.wav", "line_number": 42}

        error = STTError(
            message="Processing failed", error_code="PROCESSING_ERROR", details=details
        )

        assert error.details == details

    def test_empty_message_raises_error(self):
        """Test that empty message raises ValueError."""
        with pytest.raises(ValueError, match="message cannot be empty"):
            STTError(message="", error_code="TEST_ERROR")

    def test_empty_error_code_raises_error(self):
        """Test that empty error_code raises ValueError."""
        with pytest.raises(ValueError, match="error_code cannot be empty"):
            STTError(message="Test message", error_code="")

    def test_to_dict_method(self):
        """Test the to_dict method."""
        details = {"context": "test"}
        error = STTError(message="Test error", error_code="TEST_CODE", details=details)

        result_dict = error.to_dict()

        assert result_dict["message"] == "Test error"
        assert result_dict["error_code"] == "TEST_CODE"
        assert result_dict["details"] == details
        assert "timestamp" in result_dict
        assert isinstance(result_dict["timestamp"], str)  # Should be ISO format string
