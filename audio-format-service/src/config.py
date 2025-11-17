"""Configuration management for Audio Format Service.

This module enforces explicit configuration via environment variables.
The application will fail to start if required configuration is missing,
following the "fail-fast" principle for better error detection.
"""

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings MUST be provided via environment variables with the prefix AUDIO_FORMAT_.
    The application will fail to start if any required setting is missing.
    
    Required environment variables:
    - AUDIO_FORMAT_HOST: Server bind address (e.g., "0.0.0.0")
    - AUDIO_FORMAT_PORT: Server port (e.g., 8001)
    - AUDIO_FORMAT_RELOAD: Enable auto-reload (e.g., "false")
    - AUDIO_FORMAT_LOG_LEVEL: Logging level (e.g., "info")
    - AUDIO_FORMAT_TEMP_DIR: Temporary file directory (e.g., "/app/temp")
    - AUDIO_FORMAT_MAX_FILE_SIZE: Max upload size in bytes (e.g., 104857600)
    """

    # Server settings - NO DEFAULTS, must be explicitly set
    host: str = Field(
        ...,
        description="Server bind address (e.g., 0.0.0.0 for all interfaces)"
    )
    port: int = Field(
        ...,
        gt=0,
        lt=65536,
        description="Server port number (1-65535)"
    )
    reload: bool = Field(
        ...,
        description="Enable auto-reload for development (true/false)"
    )
    log_level: str = Field(
        ...,
        description="Logging level (debug, info, warning, error, critical)"
    )

    # File handling - NO DEFAULTS, must be explicitly set
    temp_dir: str = Field(
        ...,
        description="Directory for temporary file storage"
    )
    max_file_size: int = Field(
        ...,
        gt=0,
        description="Maximum file upload size in bytes"
    )

    class Config:
        env_prefix = "AUDIO_FORMAT_"
        case_sensitive = False


def load_settings() -> Settings:
    """Load and validate settings from environment variables.
    
    Returns:
        Settings: Validated settings object
        
    Raises:
        SystemExit: If required configuration is missing or invalid
    """
    try:
        return Settings()
    except ValidationError as e:
        # Format error message for clarity
        missing_vars = []
        invalid_vars = []
        
        for error in e.errors():
            field = error['loc'][0]
            error_type = error['type']
            env_var = f"AUDIO_FORMAT_{field.upper()}"
            
            if error_type == 'missing':
                missing_vars.append(env_var)
            else:
                invalid_vars.append(f"{env_var}: {error['msg']}")
        
        error_msg = "\n" + "="*70 + "\n"
        error_msg += "❌ CONFIGURATION ERROR: Required environment variables missing or invalid\n"
        error_msg += "="*70 + "\n\n"
        
        if missing_vars:
            error_msg += "Missing required environment variables:\n"
            for var in missing_vars:
                error_msg += f"  - {var}\n"
            error_msg += "\n"
        
        if invalid_vars:
            error_msg += "Invalid environment variable values:\n"
            for var in invalid_vars:
                error_msg += f"  - {var}\n"
            error_msg += "\n"
        
        error_msg += "Please ensure all required environment variables are set in:\n"
        error_msg += "  - docker-compose.yml (for Docker deployment)\n"
        error_msg += "  - .env file (for local development)\n"
        error_msg += "  - Environment (for direct execution)\n\n"
        error_msg += "See .env.example for required variables and their formats.\n"
        error_msg += "="*70 + "\n"
        
        print(error_msg, flush=True)
        raise SystemExit(1) from e


# Load settings on module import - will fail fast if config is missing
settings = load_settings()
