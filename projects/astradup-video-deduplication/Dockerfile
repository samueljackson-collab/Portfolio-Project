# AstraDup Video De-duplication System
# Multi-stage Docker build for production deployment

# Stage 1: Base image with system dependencies
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libchromaprint-tools \
    libsndfile1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Builder image with build dependencies
FROM base as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /tmp/requirements.txt

# Stage 3: Runtime image
FROM base as runtime

# Create app user
RUN useradd -m -u 1000 astradup && \
    mkdir -p /app /data /models && \
    chown -R astradup:astradup /app /data /models

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=astradup:astradup . /app/

# Set environment
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app:${PYTHONPATH}"

# Switch to app user
USER astradup

# Expose ports (if running API)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (override in docker-compose)
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Labels
LABEL maintainer="AstraDup Team <team@astradup.com>" \
      version="1.0.0" \
      description="AstraDup Video De-duplication System" \
      org.opencontainers.image.source="https://github.com/samueljackson-collab/Portfolio-Project"
