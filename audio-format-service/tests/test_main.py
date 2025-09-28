"""Integration tests for Audio Format Service

This module contains integration tests for the FastAPI audio format service,
testing all endpoints and their functionality.
"""

import io
import os

# Import the FastAPI app
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, '/app/shared/src')

from main import app


class TestAudioFormatService:
    """Test suite for Audio Format Service endpoints."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Import here to ensure proper path setup
        import main
        from mock_audio_format_handler import MockAudioFormatHandler

        # Initialize the handler manually for testing
        main.audio_handler = MockAudioFormatHandler()

        self.client = TestClient(app)

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "dependencies" in data
        assert "audio_handler" in data["dependencies"]

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        response = self.client.get("/formats")

        assert response.status_code == 200
        formats = response.json()
        assert isinstance(formats, list)
        assert "wav" in formats
        assert "mp3" in formats
        assert len(formats) > 0

    def test_validate_format_success(self):
        """Test successful format validation."""
        # Create a mock audio file
        mock_audio_content = b"mock audio content"
        files = {"file": ("test_audio.wav", io.BytesIO(mock_audio_content), "audio/wav")}

        response = self.client.post("/validate", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "format" in data
        assert "message" in data

    def test_validate_format_with_expected_format(self):
        """Test format validation with expected format."""
        mock_audio_content = b"mock audio content"
        files = {"file": ("test_audio.wav", io.BytesIO(mock_audio_content), "audio/wav")}
        params = {"expected_format": "wav"}

        response = self.client.post("/validate", files=files, params=params)

        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "format" in data

    def test_validate_format_no_filename(self):
        """Test format validation without filename."""
        mock_audio_content = b"mock audio content"
        files = {"file": (None, io.BytesIO(mock_audio_content), "audio/wav")}

        response = self.client.post("/validate", files=files)

        assert response.status_code == 422  # FastAPI validation error

    def test_detect_format_success(self):
        """Test successful format detection."""
        mock_audio_content = b"mock audio content"
        files = {"file": ("test_audio.mp3", io.BytesIO(mock_audio_content), "audio/mp3")}

        response = self.client.post("/detect", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "format" in data
        assert "confidence" in data
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0

    def test_detect_format_no_filename(self):
        """Test format detection without filename."""
        mock_audio_content = b"mock audio content"
        files = {"file": (None, io.BytesIO(mock_audio_content), "audio/mp3")}

        response = self.client.post("/detect", files=files)

        assert response.status_code == 422  # FastAPI validation error

    def test_get_metadata_success(self):
        """Test successful metadata extraction."""
        mock_audio_content = b"mock audio content"
        files = {"file": ("test_audio.wav", io.BytesIO(mock_audio_content), "audio/wav")}

        response = self.client.post("/metadata", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "duration" in data
        assert "sample_rate" in data
        assert "channels" in data
        assert "format" in data
        assert "size" in data
        assert isinstance(data["duration"], float)
        assert isinstance(data["sample_rate"], int)
        assert isinstance(data["channels"], int)
        assert isinstance(data["size"], int)

    def test_get_metadata_no_filename(self):
        """Test metadata extraction without filename."""
        mock_audio_content = b"mock audio content"
        files = {"file": (None, io.BytesIO(mock_audio_content), "audio/wav")}

        response = self.client.post("/metadata", files=files)

        assert response.status_code == 422  # FastAPI validation error

    def test_convert_format_success(self):
        """Test successful format conversion."""
        mock_audio_content = b"mock audio content"
        files = {"file": ("test_audio.wav", io.BytesIO(mock_audio_content), "audio/wav")}
        data = {"target_format": "mp3"}

        response = self.client.post("/convert", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "success" in result
        assert "original_format" in result
        assert "target_format" in result
        assert "message" in result
        assert result["target_format"] == "mp3"

    def test_convert_format_unsupported_target(self):
        """Test format conversion with unsupported target format."""
        mock_audio_content = b"mock audio content"
        files = {"file": ("test_audio.wav", io.BytesIO(mock_audio_content), "audio/wav")}
        data = {"target_format": "xyz"}

        response = self.client.post("/convert", files=files, data=data)

        assert response.status_code == 400
        assert "not supported" in response.json()["detail"]

    def test_convert_format_no_filename(self):
        """Test format conversion without filename."""
        mock_audio_content = b"mock audio content"
        files = {"file": (None, io.BytesIO(mock_audio_content), "audio/wav")}
        data = {"target_format": "mp3"}

        response = self.client.post("/convert", files=files, data=data)

        assert response.status_code == 422  # FastAPI validation error

    def test_download_converted_file_not_implemented(self):
        """Test download endpoint (not implemented yet)."""
        response = self.client.get("/convert/test-file-id")

        assert response.status_code == 501
        assert "not implemented" in response.json()["detail"].lower()


class TestAudioFormatServiceErrorHandling:
    """Test suite for error handling scenarios."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Import here to ensure proper path setup
        import main
        from mock_audio_format_handler import MockAudioFormatHandler

        # Initialize the handler manually for testing
        main.audio_handler = MockAudioFormatHandler()

        self.client = TestClient(app)

    def test_large_file_handling(self):
        """Test handling of large files."""
        # Create a larger mock file (1MB)
        large_content = b"x" * (1024 * 1024)
        files = {"file": ("large_audio.wav", io.BytesIO(large_content), "audio/wav")}

        response = self.client.post("/validate", files=files)

        # Should handle large files gracefully
        assert response.status_code in [200, 413, 500]  # OK, Payload Too Large, or Internal Error

    def test_empty_file_handling(self):
        """Test handling of empty files."""
        files = {"file": ("empty_audio.wav", io.BytesIO(b""), "audio/wav")}

        response = self.client.post("/validate", files=files)

        # Should handle empty files gracefully
        assert response.status_code in [200, 400]

    def test_invalid_content_type(self):
        """Test handling of files with invalid content types."""
        mock_content = b"not audio content"
        files = {"file": ("test.txt", io.BytesIO(mock_content), "text/plain")}

        response = self.client.post("/validate", files=files)

        # Should handle invalid content gracefully
        assert response.status_code in [200, 400]


class TestAudioFormatServiceIntegration:
    """Integration tests for service functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Import here to ensure proper path setup
        import main
        from mock_audio_format_handler import MockAudioFormatHandler

        # Initialize the handler manually for testing
        main.audio_handler = MockAudioFormatHandler()

        self.client = TestClient(app)

    def test_workflow_validate_then_convert(self):
        """Test complete workflow: validate then convert."""
        mock_audio_content = b"mock audio content"
        files = {"file": ("test_audio.wav", io.BytesIO(mock_audio_content), "audio/wav")}

        # First validate
        validate_response = self.client.post("/validate", files=files)
        assert validate_response.status_code == 200

        # Reset file pointer for conversion
        files = {"file": ("test_audio.wav", io.BytesIO(mock_audio_content), "audio/wav")}
        data = {"target_format": "mp3"}

        # Then convert
        convert_response = self.client.post("/convert", files=files, data=data)
        assert convert_response.status_code == 200

    def test_workflow_detect_then_metadata(self):
        """Test complete workflow: detect format then get metadata."""
        mock_audio_content = b"mock audio content"
        files = {"file": ("test_audio.flac", io.BytesIO(mock_audio_content), "audio/flac")}

        # First detect format
        detect_response = self.client.post("/detect", files=files)
        assert detect_response.status_code == 200
        detected_format = detect_response.json()["format"]

        # Reset file pointer for metadata
        files = {"file": ("test_audio.flac", io.BytesIO(mock_audio_content), "audio/flac")}

        # Then get metadata
        metadata_response = self.client.post("/metadata", files=files)
        assert metadata_response.status_code == 200
        metadata = metadata_response.json()

        # Format should match
        assert metadata["format"] == detected_format

    def test_service_startup_and_shutdown(self):
        """Test service startup and shutdown behavior."""
        # Test that service is responsive after startup
        response = self.client.get("/health")
        assert response.status_code == 200

        # Test that supported formats are available
        response = self.client.get("/formats")
        assert response.status_code == 200
        assert len(response.json()) > 0


if __name__ == "__main__":
    pytest.main([__file__])
