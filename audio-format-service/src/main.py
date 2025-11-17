"""Audio Format Service

FastAPI-based service for audio format validation, detection, and conversion.
Provides REST endpoints for audio format handling operations.
"""

from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status

# Import from shared package
from stt_shared.exceptions import AudioFormatError, ValidationError
from stt_shared.interfaces.audio_format import AudioFormatHandler

# Import from local modules
from __version__ import __version__
from config import settings
from dependencies import get_audio_handler, lifespan
from schemas import (
    AudioMetadataResponse,
    ConversionResponse,
    FormatDetectionResponse,
    FormatValidationResponse,
    HealthResponse,
)
from utils import save_upload_file_tmp


# Create FastAPI application
app = FastAPI(
    title="Audio Format Service",
    description="Service for audio format validation, detection, and conversion",
    version=__version__,
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health_check(handler: AudioFormatHandler = Depends(get_audio_handler)):
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        dependencies={
            "audio_handler": "initialized" if handler else "not_initialized",
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

    async with save_upload_file_tmp(file) as temp_file_path:
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

    async with save_upload_file_tmp(file) as temp_file_path:
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

    async with save_upload_file_tmp(file) as temp_file_path:
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

    async with save_upload_file_tmp(file) as temp_file_path:
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
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level
    )
