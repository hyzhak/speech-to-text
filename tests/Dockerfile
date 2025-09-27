FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (none needed for basic Python testing)
RUN apt-get update && rm -rf /var/lib/apt/lists/*

# Copy shared package first
COPY shared/ /app/shared/

# Install shared package in development mode
RUN pip install -e /app/shared/

# Copy test requirements and install
COPY tests/requirements.txt /app/tests/
RUN pip install -r /app/tests/requirements.txt

# Copy test files
COPY tests/ /app/tests/

# Set Python path to include shared package src directory
ENV PYTHONPATH=/app/shared/src:/app

WORKDIR /app/tests

CMD ["python", "-m", "pytest", "-v"]