# Optimized Dockerfile for FastAPI App

## Overview
Production-grade multi-stage Dockerfile optimized for FastAPI. Focuses on minimal attack surface, deterministic builds, and efficient caching.

## Build Stages
1. **Base Builder** – Python slim image with build tools, installs Poetry + dependencies.
2. **Test Stage** – Runs `pytest` and linting before producing final artifact.
3. **Runtime Stage** – Distroless or slim base containing app code, dependencies from virtualenv export, non-root user, healthcheck.

## Key Techniques
- Uses `POETRY_EXPORT` to create deterministic `requirements.txt` for runtime.
- Employs BuildKit cache mounts for pip and poetry caches.
- Multi-arch builds supported via `docker buildx bake`.
- Integrates with GitHub Actions to sign images using Cosign.

## Usage
- Build locally: `docker build -t fastapi-app -f Dockerfile .`.
- Run: `docker run -p 8000:8000 fastapi-app`.
- Bake multi-arch release: `docker buildx bake release` (configured in `docker-bake.hcl`).

## Security Hardening
- Sets `USER app` and drops capabilities.
- Enables read-only root filesystem, tempfs mounts for writable dirs.
- Leverages `pip install --no-cache-dir --only-binary` to prevent compiling malicious code.
- Includes `trivy` scan stage in CI to block vulnerabilities.

