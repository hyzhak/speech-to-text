"""Interface contract tests for SpeechToTextModel implementations.

These tests verify that any implementation of the SpeechToTextModel interface
follows the expected contract and behavior.
"""

import pytest
from abc import ABC
from datetime import datetime
import sys
import os

# Add the src directory to the path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from interfaces.stt_model import SpeechToTextModel
from models import AudioRequest, TranscriptionResult, ModelConfig


class MockSTTModel(SpeechToTextModel):
    """Mock implementation for testing the interface contract."""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self._mock_loaded = False
    
    def transcribe(self, request: AudioRequest) -> TranscriptionResult:
        """Mock transcription that returns a simple result."""
        if not self.is_loaded:
            raise Exception("Model not loaded")
        
        return TranscriptionResult(
            text="Mock transcription result",
            confidence=0.95,
            processing_time=1.0,
            model_used=self.config.model_type
        )
    
    def get_supported_formats(self) -> list:
        """Return mock supported formats."""
        return ["wav", "mp3"]
    
    def get_model_info(self) -> dict:
        """Return mock model info."""
        return {
            "name": "Mock STT Model",
            "version": "1.0.0",
            "type": self.config.model_type,
            "parameters": self.config.parameters,
            "loaded": self.is_loaded
        }
    
    def health_check(self) -> dict:
        """Return mock health status."""
        return {
            "status": "healthy" if self.is_loaded else "unhealthy",
            "message": "Mock model is ready" if self.is_loaded else "Mock model not loaded",
            "details": {"mock": True},
            "timestamp": datetime.now().isoformat()
        }
    
    def load_model(self) -> None:
        """Mock model loading."""
        self._is_loaded = True
        self._mock_loaded = True
    
    def unload_model(self) -> None:
        """Mock model unloading."""
        self._is_loaded = False
        self._mock_loaded = False


class TestSpeechToTextModelInterface:
    """Test cases for the SpeechToTextModel interface contract."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = ModelConfig(
            model_type="mock",
            model_path="/mock/path",
            parameters={"test": "value"}
        )
        self.model = MockSTTModel(self.config)
        self.audio_request = AudioRequest(
            file_path="/test/audio.wav",
            audio_format="wav"
        )
    
    def test_interface_is_abstract(self):
        """Test that SpeechToTextModel is an abstract base class."""
        assert issubclass(SpeechToTextModel, ABC)
        
        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            SpeechToTextModel(self.config)
    
    def test_initialization(self):
        """Test model initialization."""
        assert self.model.config == self.config
        assert not self.model.is_loaded
        assert hasattr(self.model, '_is_loaded')
    
    def test_load_unload_model(self):
        """Test model loading and unloading."""
        # Initially not loaded
        assert not self.model.is_loaded
        
        # Load model
        self.model.load_model()
        assert self.model.is_loaded
        
        # Unload model
        self.model.unload_model()
        assert not self.model.is_loaded
    
    def test_transcribe_requires_loaded_model(self):
        """Test that transcription requires a loaded model."""
        # Should work when loaded
        self.model.load_model()
        result = self.model.transcribe(self.audio_request)
        assert isinstance(result, TranscriptionResult)
        assert result.text == "Mock transcription result"
        assert result.model_used == "mock"
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.model.get_supported_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0
        assert all(isinstance(fmt, str) for fmt in formats)
    
    def test_get_model_info(self):
        """Test getting model information."""
        info = self.model.get_model_info()
        assert isinstance(info, dict)
        
        # Check required fields
        required_fields = ["name", "version", "type", "parameters", "loaded"]
        for field in required_fields:
            assert field in info
        
        assert info["type"] == self.config.model_type
        assert info["parameters"] == self.config.parameters
    
    def test_health_check(self):
        """Test health check functionality."""
        # Test when not loaded
        health = self.model.health_check()
        assert isinstance(health, dict)
        
        required_fields = ["status", "message", "details", "timestamp"]
        for field in required_fields:
            assert field in health
        
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert isinstance(health["message"], str)
        assert isinstance(health["details"], dict)
        assert isinstance(health["timestamp"], str)
        
        # Test when loaded
        self.model.load_model()
        health_loaded = self.model.health_check()
        assert health_loaded["status"] == "healthy"
    
    def test_validate_request_with_loaded_model(self):
        """Test request validation with loaded model."""
        self.model.load_model()
        
        # Valid request should not raise
        valid_request = AudioRequest(
            file_path="/test/audio.wav",
            audio_format="wav"  # Supported format
        )
        self.model.validate_request(valid_request)  # Should not raise
    
    def test_validate_request_with_unloaded_model(self):
        """Test request validation with unloaded model."""
        # Should raise error when model not loaded
        with pytest.raises(Exception):  # ModelLoadError when exceptions module exists
            self.model.validate_request(self.audio_request)
    
    def test_is_loaded_property(self):
        """Test the is_loaded property."""
        assert not self.model.is_loaded
        
        self.model.load_model()
        assert self.model.is_loaded
        
        self.model.unload_model()
        assert not self.model.is_loaded


class TestInterfaceContractCompliance:
    """Test that implementations must follow the interface contract."""
    
    def test_incomplete_implementation_fails(self):
        """Test that incomplete implementations cannot be instantiated."""
        
        class IncompleteModel(SpeechToTextModel):
            """Incomplete implementation missing required methods."""
            pass
        
        config = ModelConfig(model_type="mock", model_path="/test")
        
        # Should fail to instantiate due to missing abstract methods
        with pytest.raises(TypeError):
            IncompleteModel(config)
    
    def test_all_abstract_methods_must_be_implemented(self):
        """Test that all abstract methods must be implemented."""
        
        # Get all abstract methods from the interface
        abstract_methods = {
            name for name, method in SpeechToTextModel.__dict__.items()
            if getattr(method, '__isabstractmethod__', False)
        }
        
        expected_methods = {
            'transcribe',
            'get_supported_formats', 
            'get_model_info',
            'health_check',
            'load_model',
            'unload_model'
        }
        
        assert abstract_methods == expected_methods