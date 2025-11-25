# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir awscli aws-sam-cli \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM base AS runtime
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY infrastructure infrastructure
COPY src src
COPY requirements.txt requirements.txt

ENTRYPOINT ["sam"]
CMD ["validate", "-t", "infrastructure/template.yaml"]
