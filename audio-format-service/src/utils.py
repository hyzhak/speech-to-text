"""Utility functions for Audio Format Service."""

import os
import tempfile
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import UploadFile


@asynccontextmanager
async def save_upload_file_tmp(upload_file: UploadFile) -> AsyncGenerator[str, None]:
    """Save uploaded file to temporary location and clean up after use.
    
    Args:
        upload_file: FastAPI UploadFile object
        
    Yields:
        Path to the temporary file
        
    Note:
        File is automatically cleaned up after context manager exits.
    """
    # Extract file extension safely
    suffix = ""
    if upload_file.filename:
        _, ext = os.path.splitext(upload_file.filename)
        suffix = ext if ext else ""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        content = await upload_file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        yield temp_file_path
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass
