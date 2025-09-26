"""Audio Format Handler Interface

This module defines the abstract base class for audio format detection, validation, and conversion.
Handles multiple audio formats and provides conversion capabilities when needed.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class AudioFormatHandler(ABC):
    """Abstract base class for audio format detection, validation, and conversion."""
    
    SUPPORTED_FORMATS = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]
    
    @abstractmethod
    def validate_format(self, file_path: str) -> bool:
        """Validate if file format is supported.
        
        Args:
            file_path: Path to the audio file to validate
            
        Returns:
            True if format is supported, False otherwise
        """
        pass
    
    @abstractmethod
    def detect_format(self, file_path: str) -> Optional[str]:
        """Detect audio format from file headers.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Detected format string (e.g., 'wav', 'mp3') or None if undetectable
        """
        pass
    
    @abstractmethod
    async def convert_if_needed(self, file_path: str, target_format: str = "wav") -> str:
        """Convert audio to target format if needed.
        
        Args:
            file_path: Path to the source audio file
            target_format: Target format for conversion (default: 'wav')
            
        Returns:
            Path to the converted file (may be same as input if no conversion needed)
            
        Raises:
            AudioFormatError: If conversion fails
        """
        pass