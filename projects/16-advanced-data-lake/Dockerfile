# Advanced Data Lake - Production Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r datalake && useradd -r -g datalake datalake

COPY --from=builder /root/.local /home/datalake/.local

ENV PATH=/home/datalake/.local/bin:$PATH
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

COPY src/ ./src/
COPY data/ ./data/

RUN mkdir -p /data/bronze /data/silver /data/gold && \
    chown -R datalake:datalake /app /data

USER datalake

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pandas; print('healthy')" || exit 1

CMD ["python", "-m", "src.streaming_ingest"]
