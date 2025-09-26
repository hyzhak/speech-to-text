#!/usr/bin/env python3
"""Validation script to verify shared package setup is correct.

This script should be run from the shared/ directory to test the package setup.
Usage: python validate_setup.py
"""

import sys
import os
import subprocess

def test_package_installation():
    """Test that the package can be installed in development mode."""
    try:
        # Install package in development mode
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        if result.returncode != 0:
            print(f"❌ Package installation failed: {result.stderr}")
            return False
        print("✅ Package installed successfully in development mode")
        return True
    except Exception as e:
        print(f"❌ Package installation error: {e}")
        return False

def test_imports():
    """Test that all shared components can be imported correctly."""
    try:
        # Test importing the main package
        import stt_shared
        print("✅ Main package imported successfully")
        
        # Test data models
        from stt_shared import AudioRequest, TranscriptionResult, ModelConfig, STTError
        print("✅ Data models imported successfully")
        
        # Test exceptions
        from stt_shared import (
            STTException, AudioFormatError, ModelLoadError, 
            TranscriptionError, ValidationError, ConfigurationError
        )
        print("✅ Exception classes imported successfully")
        
        # Test interfaces
        from stt_shared import SpeechToTextModel, AudioFormatHandler
        print("✅ Interfaces imported successfully")
        
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