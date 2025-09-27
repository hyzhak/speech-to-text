#!/bin/bash
# Linting script using Docker and ruff

set -e

# Parse command line arguments
FIX_MODE=false
UNSAFE_FIXES=false
CHECK_ONLY=true

for arg in "$@"; do
    case $arg in
        --fix)
            FIX_MODE=true
            CHECK_ONLY=false
            ;;
        --unsafe-fixes)
            UNSAFE_FIXES=true
            ;;
        *)
            # Unknown option, pass it through to ruff
            ;;
    esac
done

echo "🔍 Running ruff linter..."

# Build the ruff linter image if it doesn't exist
if ! docker image inspect ruff-linter >/dev/null 2>&1; then
    echo "📦 Building ruff linter image..."
    docker build -f Dockerfile.ruff -t ruff-linter .
fi

# Prepare ruff command arguments
RUFF_ARGS="."
if [[ "$FIX_MODE" == "true" ]]; then
    RUFF_ARGS="$RUFF_ARGS --fix"
fi
if [[ "$UNSAFE_FIXES" == "true" ]]; then
    RUFF_ARGS="$RUFF_ARGS --unsafe-fixes"
fi

# Run ruff check
echo "🔍 Checking code with ruff..."
if [[ "$FIX_MODE" == "true" ]]; then
    if [[ "$UNSAFE_FIXES" == "true" ]]; then
        echo "🔧 Running with --fix and --unsafe-fixes options..."
    else
        echo "🔧 Running with --fix option..."
    fi
    docker run --rm -v $(pwd):/app ruff-linter ruff check $RUFF_ARGS
    echo "🎨 Formatting code with ruff..."
    docker run --rm -v $(pwd):/app ruff-linter ruff format .
    echo "✅ Linting and formatting complete!"
else
    docker run --rm -v $(pwd):/app ruff-linter ruff check $RUFF_ARGS
    if [[ $? -ne 0 ]]; then
        echo ""
        echo "ℹ️  Available options:"
        echo "   ./scripts/lint.sh --fix                    # Fix safe issues automatically"
        echo "   ./scripts/lint.sh --fix --unsafe-fixes     # Fix all issues (including unsafe ones)"
    fi
fi