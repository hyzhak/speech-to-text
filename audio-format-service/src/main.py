"""Audio Format Service

FastAPI-based service for audio format validation, detection, and conversion.
Provides REST endpoints for audio format handling operations.
"""

import os

# Import from shared package
import sys
import tempfile
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

sys.path.insert(0, '/app/shared/src')

from exceptions import AudioFormatError, ValidationError
from interfaces.audio_format import AudioFormatHandler
from mock_audio_format_handler import MockAudioFormatHandler


# Response models
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


# Global handler instance
audio_handler: Optional[AudioFormatHandler] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global audio_handler

    # Initialize audio format handler
    # Use mock handler for now - will be replaced with real implementation
    audio_handler = MockAudioFormatHandler()

    yield

    # Cleanup
    audio_handler = None


# Create FastAPI application
app = FastAPI(
    title="Audio Format Service",
    description="Service for audio format validation, detection, and conversion",
    version="1.0.0",
    lifespan=lifespan,
)


def get_audio_handler() -> AudioFormatHandler:
    """Dependency to get the audio format handler."""
    if audio_handler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audio format handler not initialized"
        )
    return audio_handler


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        dependencies={
            "audio_handler": "initialized" if audio_handler else "not_initialized",
            "ffmpeg": "available",  # TODO: Check actual ffmpeg availability
        }
    )


@app.get("/formats", response_model=List[str])
async def get_supported_formats(
    handler: AudioFormatHandler = Depends(get_audio_handler)
):
    """Get list of supported audio formats."""
    return handler.get_supported_formats()


@app.post("/validate", response_model=FormatValidationResponse)
async def validate_format(
    file: UploadFile = File(...),
    expected_format: Optional[str] = None,
    handler: AudioFormatHandler = Depends(get_audio_handler)
):
    """Validate audio file format."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename"
        )

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Validate format
        is_valid = handler.validate_format(temp_file_path, expected_format)
        detected_format = handler.detect_format(temp_file_path) if is_valid else None

        return FormatValidationResponse(
            valid=is_valid,
            format=detected_format,
            message="Format validation successful" if is_valid else "Format validation failed"
        )

    except (AudioFormatError, ValidationError) as e:
        return FormatValidationResponse(
            valid=False,
            format=None,
            message=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Format validation failed: {str(e)}"
        )

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


@app.post("/detect", response_model=FormatDetectionResponse)
async def detect_format(
    file: UploadFile = File(...),
    handler: AudioFormatHandler = Depends(get_audio_handler)
):
    """Detect audio file format."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename"
        )

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Detect format
        detected_format = handler.detect_format(temp_file_path)

        return FormatDetectionResponse(
            format=detected_format,
            confidence=0.95  # Mock confidence for now
        )

    except (AudioFormatError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Format detection failed: {str(e)}"
        )

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


@app.post("/metadata", response_model=AudioMetadataResponse)
async def get_metadata(
    file: UploadFile = File(...),
    handler: AudioFormatHandler = Depends(get_audio_handler)
):
    """Get audio file metadata."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename"
        )

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Get metadata
        metadata = handler.get_audio_metadata(temp_file_path)

        return AudioMetadataResponse(
            duration=metadata["duration"],
            sample_rate=metadata["sample_rate"],
            channels=metadata["channels"],
            bitrate=metadata.get("bitrate"),
            format=metadata["format"],
            size=metadata["size"]
        )

    except (AudioFormatError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metadata extraction failed: {str(e)}"
        )

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


@app.post("/convert", response_model=ConversionResponse)
async def convert_format(
    file: UploadFile = File(...),
    target_format: str = Form(...),
    handler: AudioFormatHandler = Depends(get_audio_handler)
):
    """Convert audio file to target format."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename"
        )

    if not handler.is_format_supported(target_format):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target format '{target_format}' is not supported"
        )

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Detect original format
        original_format = handler.detect_format(temp_file_path)

        # Convert if needed
        converted_path = await handler.convert_if_needed(temp_file_path, target_format)

        return ConversionResponse(
            success=True,
            original_format=original_format,
            target_format=target_format,
            file_path=converted_path,
            message="Conversion completed successfully"
        )

    except (AudioFormatError, ValidationError) as e:
        return ConversionResponse(
            success=False,
            original_format="unknown",
            target_format=target_format,
            file_path=None,
            message=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Format conversion failed: {str(e)}"
        )

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


@app.get("/convert/{file_id}")
async def download_converted_file(file_id: str):
    """Download converted audio file."""
    # This is a placeholder - in a real implementation, you'd:
    # 1. Validate the file_id
    # 2. Check if the file exists and is ready
    # 3. Return the file with proper headers
    # 4. Clean up the file after download

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="File download not implemented yet"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
