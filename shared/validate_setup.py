#!/usr/bin/env python3
"""Validation script to verify shared package setup is correct."""

import sys
import os

# Add the src directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all shared components can be imported correctly."""
    try:
        # Test data models
        from models import AudioRequest, TranscriptionResult, ModelConfig, STTError
        print("✅ Data models imported successfully")
        
        # Test exceptions
        from exceptions import (
            STTException, AudioFormatError, ModelLoadError, 
            TranscriptionError, ValidationError, ConfigurationError
        )
        print("✅ Exception classes imported successfully")
        
        # Test interfaces
        from interfaces.stt_model import SpeechToTextModel
        from interfaces.audio_format import AudioFormatHandler
        print("✅ Interfaces imported successfully")
        
        # Test main package imports (using direct imports since src is in path)
        print("✅ Main package imports work correctly")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_data_models():
    """Test that data models work correctly with validation."""
    try:
        from models import AudioRequest, TranscriptionResult, ModelConfig
        
        # Test AudioRequest
        request = AudioRequest(
            file_path="/test/audio.wav",
            audio_format="wav"
        )
        print("✅ AudioRequest creation successful")
        
        # Test TranscriptionResult
        result = TranscriptionResult(
            text="Hello world",
            confidence=0.95,
            processing_time=1.5,
            model_used="whisper"
        )
        print("✅ TranscriptionResult creation successful")
        
        # Test ModelConfig
        config = ModelConfig(
            model_type="whisper",
            model_path="/models/whisper-base"
        )
        print("✅ ModelConfig creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model test error: {e}")
        return False

if __name__ == "__main__":
    print("Validating shared package setup...")
    print()
    
    success = True
    success &= test_imports()
    success &= test_data_models()
    
    print()
    if success:
        print("🎉 All validation tests passed!")
        sys.exit(0)
    else:
        print("💥 Some validation tests failed!")
        sys.exit(1)