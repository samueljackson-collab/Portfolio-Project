# Real-time Collaboration Server - Production Dockerfile

FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim as production

WORKDIR /app

RUN groupadd -r collab && useradd -r -g collab collab

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY src/ ./src/

RUN chown -R collab:collab /app

USER collab

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PORT=8765 \
    HOST=0.0.0.0

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import websockets; import asyncio; asyncio.run(websockets.connect('ws://localhost:8765'))" || exit 1

CMD ["python", "-m", "collaboration_server"]
