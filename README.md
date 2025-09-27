# Modular Speech-to-Text System

A containerized, modular speech-to-text system designed for batch audio processing with a focus on flexibility and testability. The system converts audio files to text using ML models (primarily Whisper) through a microservices architecture.

## 🚨 Important: Docker-Only Development

**This project enforces Docker-only development. Do NOT use system Python or local package managers.**

All development tasks must be performed using Docker containers to ensure:
- Consistent development environment across all machines
- Proper dependency isolation
- Reproducible builds and tests
- No conflicts with system Python installations

## Key Features

- **Multi-format Audio Support**: Handles wav, mp3, mp4, m4a, flac, ogg formats with automatic conversion
- **Modular ML Models**: Plugin-based architecture allowing easy swapping between different speech-to-text implementations
- **CLI Interface**: Command-line tool for batch processing audio files
- **Containerized Services**: Docker-based microservices for scalability and isolation
- **Mock Testing**: Lightweight mock models for fast development and testing
- **Observability**: OpenTelemetry integration for monitoring and logging

## Development Workflow

### Prerequisites

- Docker and Docker Compose installed
- No Python installation required on host system

### Setup

1. Clone the repository
2. All development is done through Docker containers - no local setup needed

### Running Tests

```bash
# Run all shared package tests
docker compose -f docker-compose.test.yml up --build test-shared --abort-on-container-exit

# Run all tests
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

### Code Quality

```bash
# Check code quality (lint only)
./scripts/lint.sh

# Fix safe linting issues automatically
./scripts/lint.sh --fix

# Fix all linting issues (including unsafe ones)
./scripts/lint.sh --fix --unsafe-fixes
```

### Running Services

```bash
# Start all services
docker compose up --build

# Start specific service
docker compose up --build [service-name]

# View logs
docker compose logs -f [service-name]

# Stop services
docker compose down
```

### Development Commands

```bash
# Validate shared package setup
docker compose run --rm shared python validate_setup.py

# Run CLI tool
docker compose run --rm cli [command-options]

# Access service shell for debugging
docker compose run --rm [service-name] bash
```

## Project Structure

```
speech-to-text/
├── .git/                   # Git repository
├── .kiro/                  # Kiro IDE configuration and specs
├── cli/                    # CLI service (command-line interface)
├── stt-service/           # Core speech-to-text processing service
├── audio-format-service/  # Audio format handling service
├── shared/                # Shared libraries and interfaces
├── tests/                 # Integration and end-to-end tests
├── scripts/               # Development scripts (Docker-based)
├── data/                  # Shared data directory (runtime)
├── models/                # ML model storage (gitignored)
├── docker-compose.yml     # Service orchestration
└── docker-compose.test.yml # Test environment
```

## Architecture

The system follows a microservices architecture with:

- **Shared Package**: Common data models, interfaces, and utilities
- **CLI Service**: Command-line interface for batch processing
- **STT Service**: Core speech-to-text processing
- **Audio Format Service**: Audio format detection and conversion
- **Mock Implementations**: For testing and development

## Technology Stack

- **Python 3.11+**: Primary programming language
- **Docker & Docker Compose**: Containerization and orchestration
- **FastAPI**: Web framework for microservices
- **OpenAI Whisper**: Primary speech-to-text model
- **PyTorch & TorchAudio**: ML framework and audio processing
- **FFmpeg**: Audio format conversion
- **Pytest**: Testing framework with async support

## Contributing

1. **Always use Docker**: Never install Python packages locally
2. **Run tests**: Ensure all tests pass before committing
3. **Code quality**: Use `./scripts/lint.sh --fix` before committing
4. **Follow architecture**: Maintain separation between services
5. **Update documentation**: Keep README and specs current

## Troubleshooting

### Common Issues

**"Command not found" errors**: Make sure you're using Docker commands, not local Python

**Permission issues**: Ensure Docker has proper permissions on your system

**Port conflicts**: Check if ports 8000, 8001, etc. are available

**Build failures**: Try `docker compose down -v` to clean up volumes

### Getting Help

1. Check the `.kiro/specs/` directory for detailed specifications
2. Review service logs: `docker compose logs -f [service-name]`
3. Validate setup: `docker compose run --rm shared python validate_setup.py`

## License

This project uses only free and open source software with open ML models to ensure accessibility and transparency.