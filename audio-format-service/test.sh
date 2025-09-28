#!/bin/bash
# Test runner for audio format service

set -e

echo "🧪 Running audio format service tests..."

# Build and run tests in Docker
docker build -f audio-format-service/Dockerfile -t audio-format-service-test .

# Run tests
docker run --rm \
  -v $(pwd)/audio-format-service/tests:/app/tests \
  audio-format-service-test \
  python -m pytest tests/ -v

echo "✅ Audio format service tests completed!"