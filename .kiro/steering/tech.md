# Technology Stack

## Core Technologies

- **Python 3.8+**: Primary programming language
- **Docker & Docker Compose**: Containerization and orchestration
- **FastAPI**: Web framework for microservices
- **OpenTelemetry**: Observability and monitoring
- **uv**: Python package manager for dependency management

## ML & Audio Processing

- **OpenAI Whisper**: Primary speech-to-text model
- **PyTorch & TorchAudio**: ML framework and audio processing
- **FFmpeg**: Audio format conversion (via ffmpeg-python)
- **Mutagen**: Audio metadata extraction

## Key Dependencies

- **FastAPI + Uvicorn**: API services
- **Click**: CLI interface
- **Pydantic**: Data validation and serialization
- **Pytest**: Testing framework with async support
- **HTTPX**: HTTP client for testing

## Development Tools

- **uv**: Package management and virtual environments
- **pytest**: Unit and integration testing
- **docker-compose**: Local development orchestration
- **GitHub Actions**: CI/CD pipeline

## Common Commands

### Setup and Installation
```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install shared package in development mode
cd shared && uv pip install -e .

# Install service dependencies
cd cli && uv pip install -r requirements.txt
cd stt-service && uv pip install -r requirements.txt
```

### Development
```bash
# Run all services
docker-compose up --build

# Run tests
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Run specific service tests
cd tests && pytest -v

# Validate shared package setup
cd shared && python validate_setup.py
```

### Container Management
```bash
# Build and start services
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Clean up containers and volumes
docker-compose down -v --remove-orphans
```

## Architecture Patterns

- **Microservices**: Each service runs in isolated containers
- **Plugin Architecture**: Abstract interfaces for ML models and audio handlers
- **Dependency Injection**: Services depend on abstractions, not implementations
- **Shared Libraries**: Common models and interfaces in `shared` package