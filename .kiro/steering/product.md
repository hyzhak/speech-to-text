# Product Overview

This is a modular speech-to-text system designed for batch audio processing with a focus on flexibility and testability. The system converts audio files to text using ML models (primarily Whisper) through a containerized microservices architecture.

## Key Features

- **Multi-format Audio Support**: Handles wav, mp3, mp4, m4a, flac, ogg formats with automatic conversion
- **Modular ML Models**: Plugin-based architecture allowing easy swapping between different speech-to-text implementations
- **CLI Interface**: Command-line tool for batch processing audio files
- **Containerized Services**: Docker-based microservices for scalability and isolation
- **Mock Testing**: Lightweight mock models for fast development and testing
- **Observability**: OpenTelemetry integration for monitoring and logging

## Target Use Cases

- Batch audio file transcription
- Development and testing with mock models
- Modular architecture for different ML model implementations
- Containerized deployment scenarios

## Open Source Commitment

The system uses only free and open source software with open ML models to ensure accessibility and transparency.