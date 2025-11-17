"""Response models for Audio Format Service API."""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class FormatValidationResponse(BaseModel):
    """Response model for format validation."""

    valid: bool = Field(..., description="Whether the format is valid")
    format: Optional[str] = Field(None, description="Detected format")
    message: Optional[str] = Field(None, description="Validation message")


class FormatDetectionResponse(BaseModel):
    """Response model for format detection."""

    format: str = Field(..., description="Detected audio format")
    confidence: float = Field(..., description="Detection confidence (0.0-1.0)")


class AudioMetadataResponse(BaseModel):
    """Response model for audio metadata."""

    duration: float = Field(..., description="Duration in seconds")
    sample_rate: int = Field(..., description="Sample rate in Hz")
    channels: int = Field(..., description="Number of audio channels")
    bitrate: Optional[int] = Field(None, description="Bitrate in kbps")
    format: str = Field(..., description="Audio format")
    size: int = Field(..., description="File size in bytes")


class ConversionResponse(BaseModel):
    """Response model for format conversion."""

    success: bool = Field(..., description="Whether conversion was successful")
    original_format: str = Field(..., description="Original audio format")
    target_format: str = Field(..., description="Target audio format")
    file_path: Optional[str] = Field(None, description="Path to converted file")
    message: Optional[str] = Field(None, description="Conversion message")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    dependencies: Dict[str, str] = Field(..., description="Dependency status")
