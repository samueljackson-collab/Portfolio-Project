# MLOps Platform Dockerfile
# Multi-stage build for production model serving

FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

COPY src/ ./src/
COPY configs/ ./configs/ 2>/dev/null || true

# Create non-root user
RUN useradd --create-home --shell /bin/bash mlops && \
    chown -R mlops:mlops /app
USER mlops

ENV PYTHONPATH=/app
ENV MLFLOW_TRACKING_URI=http://mlflow:5000
ENV MODEL_NAME=default-model
ENV PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8000"]

# Training stage
FROM base as training

COPY src/ ./src/
COPY configs/ ./configs/ 2>/dev/null || true
COPY scripts/ ./scripts/ 2>/dev/null || true

ENV PYTHONPATH=/app
ENV MLFLOW_TRACKING_URI=http://mlflow:5000

CMD ["python", "-m", "src.train"]
