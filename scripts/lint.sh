#!/bin/bash
# Linting script using Docker and ruff

set -e

echo "🔍 Running ruff linter..."

# Build the ruff linter image if it doesn't exist
if ! docker image inspect ruff-linter >/dev/null 2>&1; then
    echo "📦 Building ruff linter image..."
    docker build -f Dockerfile.ruff -t ruff-linter .
fi

# Run ruff check
echo "🔍 Checking code with ruff..."
docker run --rm -v $(pwd):/app ruff-linter ruff check .

# Run ruff format
echo "🎨 Formatting code with ruff..."
docker run --rm -v $(pwd):/app ruff-linter ruff format .

echo "✅ Linting and formatting complete!"