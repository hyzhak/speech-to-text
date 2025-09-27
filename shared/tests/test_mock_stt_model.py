"""Tests for MockSpeechToTextModel

This module contains comprehensive unit tests for the MockSpeechToTextModel
implementation, covering all functionality including configurable responses,
error simulation, and interface contract compliance.
"""

import asyncio

import pytest
from exceptions import AudioFormatError, ModelLoadError, TranscriptionError
from mock_stt_model import MockSpeechToTextModel

from models import AudioRequest, ModelConfig, TranscriptionResult


class TestMockSpeechToTextModel:
    """Test suite for MockSpeechToTextModel."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.config = ModelConfig(
            model_type="mock",
            model_path="/mock/model/path",
            parameters={
                "processing_delay": 0.01,  # Fast for testing
                "error_rate": 0.0,
                "confidence_range": (0.8, 0.9),
            },
        )
        self.model = MockSpeechToTextModel(self.config)

    @pytest.mark.asyncio
    async def test_model_initialization(self):
        """Test that the mock model initializes correctly."""
        assert self.model.config == self.config
        assert not self.model.is_loaded
        assert self.model._processing_delay == 0.01
        assert self.model._error_rate == 0.0
        assert self.model._confidence_range == (0.8, 0.9)

    @pytest.mark.asyncio
    async def test_load_model_success(self):
        """Test successful model loading."""
        assert not self.model.is_loaded

        await self.model.load_model()

        assert self.model.is_loaded

    @pytest.mark.asyncio
    async def test_load_model_failure_simulation(self):
        """Test model loading failure simulation."""
        # Configure to simulate load failure
        self.model.configure_mock_behavior(simulate_load_failure=True)

        with pytest.raises(ModelLoadError) as exc_info:
            await self.model.load_model()

        assert "Mock model load failure simulation" in str(exc_info.value)
        assert not self.model.is_loaded

    @pytest.mark.asyncio
    async def test_unload_model(self):
        """Test model unloading."""
        await self.model.load_model()
        assert self.model.is_loaded

        await self.model.unload_model()

        assert not self.model.is_loaded

    def test_get_supported_formats(self):
        """Test that supported formats are returned correctly."""
        formats = self.model.get_supported_formats()

        expected_formats = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]
        assert formats == expected_formats

        # Ensure it returns a copy (not the original list)
        formats.append("test")
        assert self.model.get_supported_formats() == expected_formats

    def test_get_model_info(self):
        """Test model information retrieval."""
        info = self.model.get_model_info()

        assert info["name"] == "MockSpeechToTextModel"
        assert info["version"] == "1.0.0"
        assert info["type"] == "mock"
        assert info["loaded"] == self.model.is_loaded
        assert "supported_formats" in info
        assert "mock_responses" in info
        assert info["processing_delay"] == 0.01
        assert info["error_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """Test health check when model is healthy."""
        await self.model.load_model()

        health = await self.model.health_check()

        assert health["status"] == "healthy"
        assert "Mock model is ready" in health["message"]
        assert health["details"]["mock_model"] is True
        assert health["details"]["loaded"] is True
        assert "timestamp" in health

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self):
        """Test health check when model is not loaded."""
        health = await self.model.health_check()

        assert health["status"] == "unhealthy"
        assert "Mock model not loaded" in health["message"]
        assert health["details"]["loaded"] is False

    @pytest.mark.asyncio
    async def test_health_check_degraded_simulation(self):
        """Test health check with degraded status simulation."""
        await self.model.load_model()
        self.model.configure_mock_behavior(simulate_health_issues=True)

        health = await self.model.health_check()

        assert health["status"] == "degraded"
        assert "Mock health issue simulation" in health["message"]
        assert health["details"]["simulated"] is True

    @pytest.mark.asyncio
    async def test_transcribe_success(self):
        """Test successful transcription."""
        await self.model.load_model()

        request = AudioRequest(file_path="/test/audio.wav", audio_format="wav")

        result = await self.model.transcribe(request)

        assert isinstance(result, TranscriptionResult)
        assert result.text == "This is a mock transcription result."
        assert 0.8 <= result.confidence <= 0.9
        assert result.processing_time > 0
        assert result.model_used == "mock-mock"
        assert result.metadata["mock_model"] is True
        assert result.metadata["file_path"] == "/test/audio.wav"

    @pytest.mark.asyncio
    async def test_transcribe_model_not_loaded(self):
        """Test transcription when model is not loaded."""
        request = AudioRequest(file_path="/test/audio.wav", audio_format="wav")

        with pytest.raises(ModelLoadError) as exc_info:
            await self.model.transcribe(request)

        assert "Model must be loaded before processing requests" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_transcribe_unsupported_format(self):
        """Test transcription with unsupported audio format."""
        await self.model.load_model()

        # The AudioRequest validation will catch this before it gets to the model
        with pytest.raises(ValueError) as exc_info:
            AudioRequest(file_path="/test/audio.xyz", audio_format="xyz")

        assert "Unsupported audio format: xyz" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_model_format_validation(self):
        """Test model-level format validation by bypassing AudioRequest validation."""
        await self.model.load_model()

        # Create a request with a format that passes AudioRequest validation
        # but is not supported by this specific model instance
        request = AudioRequest(file_path="/test/audio.wav", audio_format="wav")

        # Temporarily modify the model's supported formats to test validation
        original_formats = self.model._supported_formats
        self.model._supported_formats = ["mp3"]  # Only support mp3

        try:
            with pytest.raises(AudioFormatError) as exc_info:
                await self.model.transcribe(request)

            assert "Audio format 'wav' not supported" in str(exc_info.value)
        finally:
            # Restore original formats
            self.model._supported_formats = original_formats

    @pytest.mark.asyncio
    async def test_transcribe_error_simulation(self):
        """Test transcription error simulation."""
        await self.model.load_model()
        self.model.configure_mock_behavior(error_rate=1.0)  # Always fail

        request = AudioRequest(file_path="/test/audio.wav", audio_format="wav")

        with pytest.raises(TranscriptionError) as exc_info:
            await self.model.transcribe(request)

        assert "Mock transcription error simulation" in str(exc_info.value)
        assert exc_info.value.details["simulated"] is True

    @pytest.mark.asyncio
    async def test_transcribe_pattern_based_responses(self):
        """Test pattern-based response selection."""
        await self.model.load_model()

        # Test empty response pattern
        request_empty = AudioRequest(
            file_path="/test/empty_audio.wav", audio_format="wav"
        )
        result_empty = await self.model.transcribe(request_empty)
        assert result_empty.text == ""

        # Test long response pattern
        request_long = AudioRequest(
            file_path="/test/long_audio.wav", audio_format="wav"
        )
        result_long = await self.model.transcribe(request_long)
        assert "very long mock transcription" in result_long.text

    @pytest.mark.asyncio
    async def test_configure_mock_behavior(self):
        """Test runtime configuration of mock behavior."""
        # Test processing delay configuration
        self.model.configure_mock_behavior(processing_delay=0.05)
        assert self.model._processing_delay == 0.05

        # Test error rate configuration
        self.model.configure_mock_behavior(error_rate=0.5)
        assert self.model._error_rate == 0.5

        # Test confidence range configuration
        self.model.configure_mock_behavior(confidence_range=(0.7, 0.8))
        assert self.model._confidence_range == (0.7, 0.8)

        # Test custom responses
        custom_responses = {"test": "Custom test response"}
        self.model.configure_mock_behavior(custom_responses=custom_responses)
        assert "test" in self.model._mock_responses
        assert self.model._mock_responses["test"] == "Custom test response"

    def test_add_mock_response(self):
        """Test adding custom mock responses."""
        self.model.add_mock_response("custom", "Custom response text")

        assert "custom" in self.model._mock_responses
        assert self.model._mock_responses["custom"] == "Custom response text"

    def test_reset_to_defaults(self):
        """Test resetting mock behavior to defaults."""
        # Modify behavior
        self.model.configure_mock_behavior(
            processing_delay=1.0, error_rate=0.8, confidence_range=(0.1, 0.2)
        )
        self.model.add_mock_response("temp", "Temporary response")

        # Reset to defaults
        self.model.reset_to_defaults()

        assert self.model._processing_delay == 0.01  # From config
        assert self.model._error_rate == 0.0  # From config
        assert self.model._confidence_range == (0.8, 0.9)  # From config
        assert "temp" not in self.model._mock_responses

    def test_get_response_key_patterns(self):
        """Test response key pattern matching."""
        # Test default pattern
        assert self.model._get_response_key("/test/normal.wav") == "default"

        # Test empty pattern
        assert self.model._get_response_key("/test/empty_file.wav") == "empty"
        assert self.model._get_response_key("/test/silent.wav") == "empty"

        # Test long pattern
        assert self.model._get_response_key("/test/long_audio.wav") == "long"
        assert self.model._get_response_key("/test/extended.wav") == "long"

        # Test custom pattern
        self.model.add_mock_response("special", "Special response")
        assert self.model._get_response_key("/test/special_file.wav") == "special"

    @pytest.mark.asyncio
    async def test_processing_delay_timing(self):
        """Test that processing delay is actually applied."""
        await self.model.load_model()
        self.model.configure_mock_behavior(processing_delay=0.1)

        request = AudioRequest(file_path="/test/audio.wav", audio_format="wav")

        start_time = asyncio.get_event_loop().time()
        result = await self.model.transcribe(request)
        end_time = asyncio.get_event_loop().time()

        # Should take at least the processing delay time
        assert (end_time - start_time) >= 0.1
        assert result.processing_time >= 0.1

    @pytest.mark.asyncio
    async def test_confidence_range_validation(self):
        """Test that confidence values stay within configured range."""
        await self.model.load_model()

        # Test multiple transcriptions to check range
        request = AudioRequest(file_path="/test/audio.wav", audio_format="wav")

        for _ in range(10):
            result = await self.model.transcribe(request)
            assert 0.8 <= result.confidence <= 0.9

    def test_interface_contract_compliance(self):
        """Test that MockSpeechToTextModel properly implements the interface."""
        from interfaces.stt_model import SpeechToTextModel

        assert isinstance(self.model, SpeechToTextModel)

        # Check that all abstract methods are implemented
        abstract_methods = [
            "transcribe",
            "get_supported_formats",
            "get_model_info",
            "health_check",
            "load_model",
            "unload_model",
        ]

        for method_name in abstract_methods:
            assert hasattr(self.model, method_name)
            assert callable(getattr(self.model, method_name))

    @pytest.mark.asyncio
    async def test_metadata_consistency(self):
        """Test that metadata is consistently populated."""
        await self.model.load_model()

        request = AudioRequest(file_path="/test/metadata_test.wav", audio_format="wav")

        result = await self.model.transcribe(request)

        # Check required metadata fields
        assert "mock_model" in result.metadata
        assert "response_key" in result.metadata
        assert "simulated_delay" in result.metadata
        assert "file_path" in result.metadata

        assert result.metadata["mock_model"] is True
        assert result.metadata["file_path"] == request.file_path


# Integration test for error rate behavior
class TestMockModelErrorSimulation:
    """Test suite for error simulation behavior."""

    @pytest.mark.asyncio
    async def test_error_rate_statistics(self):
        """Test that error rate approximately matches configured rate."""
        config = ModelConfig(
            model_type="mock",
            model_path="/mock/path",
            parameters={"error_rate": 0.3, "processing_delay": 0.001},
        )
        model = MockSpeechToTextModel(config)
        await model.load_model()

        request = AudioRequest(file_path="/test/audio.wav", audio_format="wav")

        # Run multiple transcriptions and count errors
        total_runs = 100
        error_count = 0

        for _ in range(total_runs):
            try:
                await model.transcribe(request)
            except TranscriptionError:
                error_count += 1

        # Error rate should be approximately 30% (±10% tolerance)
        error_rate = error_count / total_runs
        assert 0.2 <= error_rate <= 0.4, (
            f"Error rate {error_rate} not within expected range"
        )


if __name__ == "__main__":
    pytest.main([__file__])
