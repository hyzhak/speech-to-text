"""Mock Speech-to-Text Model Implementation

This module provides a mock implementation of the SpeechToTextModel interface
for testing purposes. It allows configurable responses, delays, and error
simulation to facilitate comprehensive testing of the speech-to-text system.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List

from exceptions import ModelLoadError, TranscriptionError
from interfaces.stt_model import SpeechToTextModel

from models import AudioRequest, ModelConfig, TranscriptionResult


class MockSpeechToTextModel(SpeechToTextModel):
    """Mock implementation of SpeechToTextModel for testing.

    This mock model provides configurable responses, processing delays,
    and error simulation capabilities for comprehensive testing scenarios.
    """

    def __init__(self, config: ModelConfig):
        """Initialize the mock model with configuration.

        Args:
            config: Model configuration containing mock-specific parameters
        """
        super().__init__(config)

        # Default mock responses for different scenarios
        self._mock_responses = {
            "default": "This is a mock transcription result.",
            "empty": "",
            "long": "This is a very long mock transcription result that simulates "
            "processing of lengthy audio files with multiple sentences and "
            "complex content to test system behavior with larger outputs.",
        }

        # Configure mock behavior from parameters
        params = config.parameters
        self._processing_delay = params.get("processing_delay", 0.1)  # seconds
        self._error_rate = params.get("error_rate", 0.0)  # 0.0 to 1.0
        self._confidence_range = params.get("confidence_range", (0.85, 0.95))
        self._custom_responses = params.get("custom_responses", {})
        self._simulate_load_failure = params.get("simulate_load_failure", False)
        self._simulate_health_issues = params.get("simulate_health_issues", False)

        # Merge custom responses with defaults
        self._mock_responses.update(self._custom_responses)

        # Supported formats (same as real models for consistency)
        self._supported_formats = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]

    async def transcribe(self, request: AudioRequest) -> TranscriptionResult:
        """Transcribe audio to text using mock responses.

        Args:
            request: Audio request containing file path and processing options

        Returns:
            TranscriptionResult with mock transcription data

        Raises:
            TranscriptionError: If error simulation is triggered
            AudioFormatError: If audio format is not supported
            ModelLoadError: If model is not loaded
        """
        # Validate request first
        self.validate_request(request)

        # Simulate processing delay
        if self._processing_delay > 0:
            await asyncio.sleep(self._processing_delay)

        # Simulate random errors based on error rate
        import random

        if random.random() < self._error_rate:
            raise TranscriptionError(
                "Mock transcription error simulation",
                details={"file_path": request.file_path, "simulated": True},
            )

        # Determine response based on file path or use default
        response_key = self._get_response_key(request.file_path)
        mock_text = self._mock_responses.get(
            response_key, self._mock_responses["default"]
        )

        # Generate mock confidence score
        min_conf, max_conf = self._confidence_range
        confidence = random.uniform(min_conf, max_conf)

        # Calculate processing time (including simulated delay)
        processing_time = self._processing_delay + random.uniform(0.01, 0.05)

        return TranscriptionResult(
            text=mock_text,
            confidence=confidence,
            processing_time=processing_time,
            model_used=f"mock-{self.config.model_type}",
            metadata={
                "mock_model": True,
                "response_key": response_key,
                "simulated_delay": self._processing_delay,
                "file_path": request.file_path,
            },
        )

    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats.

        Returns:
            List of supported audio format extensions
        """
        return self._supported_formats.copy()

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the mock model.

        Returns:
            Dictionary containing mock model information
        """
        return {
            "name": "MockSpeechToTextModel",
            "version": "1.0.0",
            "type": "mock",
            "parameters": self.config.parameters,
            "loaded": self._is_loaded,
            "supported_formats": self._supported_formats,
            "mock_responses": list(self._mock_responses.keys()),
            "processing_delay": self._processing_delay,
            "error_rate": self._error_rate,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the mock model.

        Returns:
            Dictionary containing health status information
        """
        if self._simulate_health_issues:
            return {
                "status": "degraded",
                "message": "Mock health issue simulation",
                "details": {
                    "simulated": True,
                    "loaded": self._is_loaded,
                    "timestamp": datetime.now().isoformat(),
                },
                "timestamp": datetime.now().isoformat(),
            }

        status = "healthy" if self._is_loaded else "unhealthy"
        message = "Mock model is ready" if self._is_loaded else "Mock model not loaded"

        return {
            "status": status,
            "message": message,
            "details": {
                "mock_model": True,
                "loaded": self._is_loaded,
                "error_rate": self._error_rate,
                "processing_delay": self._processing_delay,
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def load_model(self) -> None:
        """Load the mock model into memory.

        Raises:
            ModelLoadError: If load failure simulation is enabled
        """
        if self._simulate_load_failure:
            raise ModelLoadError(
                "Mock model load failure simulation",
                details={"simulated": True, "config": self.config.model_path},
            )

        # Simulate loading delay
        if self._processing_delay > 0:
            await asyncio.sleep(self._processing_delay * 0.5)

        self._is_loaded = True

    async def unload_model(self) -> None:
        """Unload the mock model from memory."""
        # Simulate unloading delay
        if self._processing_delay > 0:
            await asyncio.sleep(self._processing_delay * 0.2)

        self._is_loaded = False

    def _get_response_key(self, file_path: str) -> str:
        """Determine which mock response to use based on file path.

        Args:
            file_path: Path to the audio file

        Returns:
            Key for the mock response to use
        """
        # Extract filename for pattern matching
        filename = (
            file_path.lower().split("/")[-1] if "/" in file_path else file_path.lower()
        )

        # Pattern-based response selection
        if "empty" in filename or "silent" in filename:
            return "empty"
        elif "long" in filename or "extended" in filename:
            return "long"
        elif any(key in filename for key in self._custom_responses.keys()):
            # Find first matching custom response key
            for key in self._custom_responses.keys():
                if key in filename:
                    return key

        return "default"

    def configure_mock_behavior(self, **kwargs) -> None:
        """Configure mock behavior at runtime.

        Args:
            **kwargs: Configuration parameters to update
        """
        if "processing_delay" in kwargs:
            self._processing_delay = kwargs["processing_delay"]
        if "error_rate" in kwargs:
            self._error_rate = max(0.0, min(1.0, kwargs["error_rate"]))
        if "confidence_range" in kwargs:
            self._confidence_range = kwargs["confidence_range"]
        if "custom_responses" in kwargs:
            self._custom_responses.update(kwargs["custom_responses"])
            self._mock_responses.update(self._custom_responses)
        if "simulate_load_failure" in kwargs:
            self._simulate_load_failure = kwargs["simulate_load_failure"]
        if "simulate_health_issues" in kwargs:
            self._simulate_health_issues = kwargs["simulate_health_issues"]

    def add_mock_response(self, key: str, response: str) -> None:
        """Add a custom mock response.

        Args:
            key: Response key (used for pattern matching in file names)
            response: Mock transcription text to return
        """
        self._mock_responses[key] = response
        self._custom_responses[key] = response

    def reset_to_defaults(self) -> None:
        """Reset mock behavior to default configuration."""
        params = self.config.parameters
        self._processing_delay = params.get("processing_delay", 0.1)
        self._error_rate = params.get("error_rate", 0.0)
        self._confidence_range = params.get("confidence_range", (0.85, 0.95))
        self._simulate_load_failure = params.get("simulate_load_failure", False)
        self._simulate_health_issues = params.get("simulate_health_issues", False)

        # Reset to original responses
        self._mock_responses = {
            "default": "This is a mock transcription result.",
            "empty": "",
            "long": "This is a very long mock transcription result that simulates "
            "processing of lengthy audio files with multiple sentences and "
            "complex content to test system behavior with larger outputs.",
        }
        self._custom_responses = params.get("custom_responses", {})
        self._mock_responses.update(self._custom_responses)
