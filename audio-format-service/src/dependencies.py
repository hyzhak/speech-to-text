"""Dependency injection and application lifespan management."""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status

from stt_shared.interfaces.audio_format import AudioFormatHandler
from stt_shared.mock_audio_format_handler import MockAudioFormatHandler

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


def get_audio_handler() -> AudioFormatHandler:
    """Dependency to get the audio format handler."""
    if audio_handler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audio format handler not initialized"
        )
    return audio_handler
