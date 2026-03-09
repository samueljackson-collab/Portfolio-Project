# Quantum-Safe Cryptography Service - Production Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies including liboqs requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    ninja-build \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Build and install liboqs
RUN git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git && \
    cd liboqs && \
    mkdir build && cd build && \
    cmake -GNinja -DBUILD_SHARED_LIBS=ON .. && \
    ninja && ninja install && \
    ldconfig

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Copy liboqs from builder
COPY --from=builder /usr/local/lib/liboqs* /usr/local/lib/
RUN ldconfig

RUN groupadd -r crypto && useradd -r -g crypto crypto

COPY --from=builder /root/.local /home/crypto/.local

ENV PATH=/home/crypto/.local/bin:$PATH
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

COPY src/ ./src/

RUN chown -R crypto:crypto /app

USER crypto

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
