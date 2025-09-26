"""Audio Format Handler Interface

This module defines the interface for audio format detection, validation, and conversion.
Handles multiple audio formats and provides conversion capabilities when needed.
"""

from typing import List, Optional


class AudioFormatHandler:
    """Handler for audio format detection, validation, and conversion."""
    
    SUPPORTED_FORMATS = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]
    
    @staticmethod
    def validate_format(file_path: str) -> bool:
        """Validate if file format is supported.
        
        Args:
            file_path: Path to the audio file to validate
            
        Returns:
            True if format is supported, False otherwise
        """
        pass
    
    @staticmethod
    def detect_format(file_path: str) -> Optional[str]:
        """Detect audio format from file headers.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Detected format string (e.g., 'wav', 'mp3') or None if undetectable
        """
        pass
    
    @staticmethod
    async def convert_if_needed(file_path: str, target_format: str = "wav") -> str:
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