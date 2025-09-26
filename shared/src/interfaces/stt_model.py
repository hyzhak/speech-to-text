"""Speech-to-Text Model Interface

This module defines the abstract base class for all speech-to-text model implementations.
All ML models must implement this interface to ensure consistent behavior across the system.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SpeechToTextModel(ABC):
    """Abstract base class for speech-to-text model implementations."""
    
    @abstractmethod
    async def transcribe(self, audio_path: str, audio_format: str = None) -> str:
        """Convert audio file to text.
        
        Args:
            audio_path: Path to the audio file to transcribe
            audio_format: Optional format hint for the audio file
            
        Returns:
            Transcribed text from the audio file
            
        Raises:
            STTError: If transcription fails
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return list of natively supported audio formats.
        
        Returns:
            List of supported audio format extensions (e.g., ['wav', 'mp3'])
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata and capabilities.
        
        Returns:
            Dictionary containing model information such as name, version, capabilities
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Verify model is ready for processing.
        
        Returns:
            True if model is healthy and ready, False otherwise
        """
        pass