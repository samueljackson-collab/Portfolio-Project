# P09 — Cloud-Native POC Deployment

## Overview
Cloud-native proof-of-concept application using FastAPI, SQLite, and Docker containerization. Demonstrates modern microservice architecture, 12-factor app principles, container orchestration, and production-ready deployment practices.

## Key Outcomes
- [x] FastAPI REST API with CRUD operations
- [x] SQLite database with SQLAlchemy ORM
- [x] Docker containerization with multi-stage builds
- [x] Docker Compose for local development
- [x] Health check endpoints (/health, /ready)
- [x] Structured logging and error handling
- [x] pytest test suite with 90%+ coverage

## Architecture
- **Components**: FastAPI app, SQLite DB, Docker, Uvicorn ASGI server
- **Patterns**: Repository pattern, dependency injection, 12-factor app
- **Dependencies**: Python 3.11+, Docker 24+, Docker Compose

```mermaid
flowchart TB
    Client[API Client]
    LB[Load Balancer<br/>NGINX]

    subgraph Container[Docker Container]
        API[FastAPI App<br/>:8000]
        DB[(SQLite DB)]
    end

    subgraph Endpoints
        Health[GET /health]
        Ready[GET /ready]
        Items[/api/items CRUD]
    end

    Client --> LB --> API
    API --> Health & Ready & Items
    API --> DB

    style Container fill:#e1f5ff
    style DB fill:#fff4e6
```

## Quickstart

```bash
make setup
make build
make run
# Visit http://localhost:8000/docs for API documentation
```

## Configuration

| Env Var | Purpose | Example | Required |
|---------|---------|---------|----------|
| `DATABASE_URL` | SQLite database path | `sqlite:///./data/app.db` | No (default) |
| `LOG_LEVEL` | Logging verbosity | `INFO`, `DEBUG` | No (default: `INFO`) |
| `API_PORT` | API server port | `8000` | No (default: `8000`) |
| `WORKERS` | Uvicorn workers | `4` | No (default: `1`) |

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run tests in Docker
make test-docker
```

## Operations

### Logs, Metrics, Traces
- **Application Logs**: Structured JSON logs to stdout
- **Health Checks**: `GET /health` (liveness), `GET /ready` (readiness)
- **Metrics**: Request latency, error rates (Prometheus format at `/metrics`)

### Common Issues & Fixes

**Issue**: Container fails to start with database error
**Fix**: Ensure data volume is mounted correctly, check permissions.

**Issue**: API returns 500 errors
**Fix**: Check logs: `docker logs <container-id>`, verify database connection.

## Security

### Secrets Handling
- Use environment variables for configuration
- Never commit `.env` files
- Use Docker secrets in production

### Container Security
- Multi-stage builds (minimal attack surface)
- Non-root user in container
- Read-only filesystem where possible

## Roadmap

- [ ] Add PostgreSQL support
- [ ] Implement Redis caching
- [ ] Add OpenTelemetry tracing
- [ ] Deploy to Kubernetes
- [ ] Add CI/CD with GitHub Actions

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [12-Factor App](https://12factor.net/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
