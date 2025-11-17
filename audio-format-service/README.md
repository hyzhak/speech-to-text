# Audio Format Service

FastAPI-based microservice for audio format validation, detection, conversion, and metadata extraction.

## Features

- 🎵 **Format Detection**: Automatically detect audio file formats
- ✅ **Format Validation**: Validate audio files against expected formats
- 🔄 **Format Conversion**: Convert between supported audio formats
- 📊 **Metadata Extraction**: Extract comprehensive audio file metadata
- 🏥 **Health Monitoring**: Built-in health check endpoint
- 🐳 **Docker Ready**: Fully containerized with Docker support

## Supported Formats

- WAV
- MP3
- MP4
- M4A
- FLAC
- OGG

## Configuration

⚠️ **IMPORTANT**: All configuration is **REQUIRED** via environment variables. The service will **fail to start** with a clear error message if any required variable is missing.

This "fail-fast" approach ensures configuration errors are caught immediately rather than causing subtle runtime issues.

### Environment Variables (ALL REQUIRED)

| Variable | Default | Description |
|----------|---------|-------------|
| `AUDIO_FORMAT_HOST` | `0.0.0.0` | Server bind address |
| `AUDIO_FORMAT_PORT` | `8001` | Server port |
| `AUDIO_FORMAT_RELOAD` | `false` | Enable auto-reload (dev only) |
| `AUDIO_FORMAT_LOG_LEVEL` | `info` | Logging level (debug, info, warning, error) |
| `AUDIO_FORMAT_TEMP_DIR` | `/app/temp` | Temporary file directory |
| `AUDIO_FORMAT_MAX_FILE_SIZE` | `104857600` | Max upload size in bytes (100MB) |

### Configuration Methods

**All variables MUST be set** - the application will not start without them.

1. **Docker Compose** (recommended - all variables pre-configured):
   ```bash
   docker-compose up
   # All required variables are set in docker-compose.yml
   ```

2. **`.env` File** (for local development):
   ```bash
   cp .env.example .env
   # All required variables are in .env.example
   python src/main.py
   ```

3. **Environment Variables** (for custom deployments):
   ```bash
   export AUDIO_FORMAT_HOST=0.0.0.0
   export AUDIO_FORMAT_PORT=8001
   export AUDIO_FORMAT_RELOAD=false
   export AUDIO_FORMAT_LOG_LEVEL=info
   export AUDIO_FORMAT_TEMP_DIR=/app/temp
   export AUDIO_FORMAT_MAX_FILE_SIZE=104857600
   python src/main.py
   ```

### What Happens if Configuration is Missing?

The application will **fail immediately** with a clear error message:

```
======================================================================
❌ CONFIGURATION ERROR: Required environment variables missing or invalid
======================================================================

Missing required environment variables:
  - AUDIO_FORMAT_PORT
  - AUDIO_FORMAT_LOG_LEVEL

Please ensure all required environment variables are set in:
  - docker-compose.yml (for Docker deployment)
  - .env file (for local development)
  - Environment (for direct execution)

See .env.example for required variables and their formats.
======================================================================
```

This "fail-fast" approach prevents the service from starting with incorrect or missing configuration.

## Quick Start

### Local Development

1. Install dependencies:
   ```bash
   cd audio-format-service
   pip install -r requirements.txt
   ```

2. Set environment variables (optional):
   ```bash
   export AUDIO_FORMAT_RELOAD=true
   export AUDIO_FORMAT_LOG_LEVEL=debug
   ```

3. Run the service:
   ```bash
   python src/main.py
   ```

4. Access the API:
   - API: http://localhost:8001
   - Docs: http://localhost:8001/docs
   - Health: http://localhost:8001/health

### Docker Deployment

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Or build and run manually:
   ```bash
   docker build -f audio-format-service/Dockerfile -t audio-format-service .
   docker run -p 8001:8001 audio-format-service
   ```

### Custom Port Example

To run on a different port:

```bash
# Using environment variable
export AUDIO_FORMAT_PORT=8002
docker-compose up

# Or inline
AUDIO_FORMAT_PORT=8002 docker-compose up
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Get Supported Formats
```bash
GET /formats
```

### Validate Format
```bash
POST /validate
Content-Type: multipart/form-data

file: <audio_file>
expected_format: wav (optional)
```

### Detect Format
```bash
POST /detect
Content-Type: multipart/form-data

file: <audio_file>
```

### Get Metadata
```bash
POST /metadata
Content-Type: multipart/form-data

file: <audio_file>
```

### Convert Format
```bash
POST /convert
Content-Type: multipart/form-data

file: <audio_file>
target_format: mp3
```

## Testing

Run tests:
```bash
cd audio-format-service
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Architecture

```
audio-format-service/
├── src/
│   ├── __init__.py
│   ├── __version__.py      # Version info
│   ├── config.py           # Configuration management
│   ├── dependencies.py     # DI and lifespan
│   ├── main.py            # FastAPI application
│   ├── schemas.py         # Response models
│   └── utils.py           # Utility functions
├── tests/
│   └── test_main.py       # Integration tests
├── Dockerfile
└── requirements.txt
```

## Development

### Code Organization

- **config.py**: Centralized configuration using pydantic-settings
- **dependencies.py**: Dependency injection and application lifespan
- **schemas.py**: Pydantic models for API responses
- **utils.py**: Reusable utility functions
- **main.py**: FastAPI routes and application setup

### Adding New Features

1. Add configuration to `config.py` if needed
2. Define response models in `schemas.py`
3. Add utility functions to `utils.py`
4. Implement endpoints in `main.py`
5. Add tests to `tests/test_main.py`

## Troubleshooting

### Port Already in Use

If port 8001 is already in use:
```bash
AUDIO_FORMAT_PORT=8002 docker-compose up
```

### File Upload Issues

Check the `AUDIO_FORMAT_MAX_FILE_SIZE` setting if uploads fail:
```bash
export AUDIO_FORMAT_MAX_FILE_SIZE=209715200  # 200MB
```

### Debug Mode

Enable debug logging:
```bash
export AUDIO_FORMAT_LOG_LEVEL=debug
export AUDIO_FORMAT_RELOAD=true
```

## License

MIT
