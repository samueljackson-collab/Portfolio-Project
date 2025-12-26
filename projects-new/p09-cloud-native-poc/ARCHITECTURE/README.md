# Architecture

## Components
- **FastAPI Producer**: CRUD-style todo service with OpenAPI docs and Prometheus endpoint.
- **Worker/Consumer**: Periodic health checker and synthetic load generator.
- **Postgres (optional)**: Replace in-memory store when running in Kubernetes overlay.

```
[Client] -> [FastAPI Service] -> [Data Store]
                      \-> [Metrics -> Prometheus]
```

## Deployment
- **Local**: Python app with uvicorn.
- **Docker/Compose**: Multi-service stack with Postgres and consumer worker.
- **Kubernetes**: Deployment + Service; optional HPA and ConfigMap for feature flags.

## Security
- Liveness/readiness probes enable safe rollout.
- API key header (`X-API-Key`) validated when `API_KEY` env var set.
