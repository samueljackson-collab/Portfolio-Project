# Kubernetes Operators - Production Dockerfile
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

# Create non-root user
RUN groupadd -r operator && useradd -r -g operator -u 65534 operator

COPY --from=builder /root/.local /home/operator/.local

ENV PATH=/home/operator/.local/bin:$PATH
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

COPY src/ ./src/

RUN chown -R operator:operator /app

USER operator

# Kopf provides its own health endpoint
EXPOSE 8080

ENTRYPOINT ["kopf", "run"]
CMD ["--verbose", "--liveness=http://0.0.0.0:8080/healthz", "/app/src/operator.py"]
