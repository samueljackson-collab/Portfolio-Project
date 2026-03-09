# Edge AI Inference Platform - Production Dockerfile
# Multi-stage build optimized for edge devices

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage - NVIDIA CUDA for GPU support
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 as production

WORKDIR /app

# Install Python and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.11 /usr/bin/python

# Create non-root user
RUN groupadd -r inference && useradd -r -g inference inference

# Copy Python packages from builder
COPY --from=builder /root/.local /home/inference/.local

# Set environment
ENV PATH=/home/inference/.local/bin:$PATH
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV MODELS_DIR=/app/models
ENV CACHE_MAX_MODELS=5
ENV CACHE_MAX_MEMORY_MB=2048

# Copy application code
COPY src/ ./src/
COPY models/ ./models/

# Create models directory
RUN mkdir -p /app/models && chown -R inference:inference /app

USER inference

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]

# CPU-only stage for edge devices without GPU
FROM python:3.11-slim as cpu-only

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r inference && useradd -r -g inference inference

# Copy Python packages from builder
COPY --from=builder /root/.local /home/inference/.local

# Set environment
ENV PATH=/home/inference/.local/bin:$PATH
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV MODELS_DIR=/app/models

# Copy application code
COPY src/ ./src/
COPY models/ ./models/

RUN mkdir -p /app/models && chown -R inference:inference /app

USER inference

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
