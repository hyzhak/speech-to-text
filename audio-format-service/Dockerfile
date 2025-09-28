FROM python:3.11-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy shared package first (for better caching)
COPY shared/ /app/shared/

# Install shared package
RUN pip install -e /app/shared/

# Copy service requirements and install dependencies
COPY audio-format-service/requirements.txt /app/
# Install dependencies excluding the shared package (already installed)
RUN grep -v "^-e ../shared" requirements.txt > requirements_docker.txt && \
    pip install -r requirements_docker.txt

# Copy service source code
COPY audio-format-service/src/ /app/src/

# Create directory for temporary files
RUN mkdir -p /app/temp

# Set environment variables
ENV PYTHONPATH=/app/src
ENV TEMP_DIR=/app/temp

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["python", "src/main.py"]