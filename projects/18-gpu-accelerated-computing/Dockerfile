# GPU-Accelerated Computing Platform - Production Dockerfile
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04 as builder

WORKDIR /app

# Install Python and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.11 /usr/bin/python

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.11 /usr/bin/python

RUN groupadd -r gpu && useradd -r -g gpu gpu

COPY --from=builder /root/.local /home/gpu/.local

ENV PATH=/home/gpu/.local/bin:$PATH
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

COPY src/ ./src/

RUN chown -R gpu:gpu /app

USER gpu

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import cupy; cupy.cuda.runtime.getDeviceCount()" || exit 1

CMD ["python", "-m", "src.portfolio_simulation"]
