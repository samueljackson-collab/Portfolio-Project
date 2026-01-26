# P09 — Cloud-Native POC Deployment

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


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


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Kubernetes Resources

#### 1. Deployment Manifest
```
Create a Kubernetes Deployment manifest for a microservice with 3 replicas, resource limits (500m CPU, 512Mi memory), readiness/liveness probes, and rolling update strategy
```

#### 2. Helm Chart
```
Generate a Helm chart for deploying a web application with configurable replicas, ingress, service, and persistent volume claims, including values for dev/staging/prod environments
```

#### 3. Custom Operator
```
Write a Kubernetes operator in Go that watches for a custom CRD and automatically creates associated ConfigMaps, Secrets, and Services based on the custom resource spec
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables

## Evidence & Verification

Verification summary: Evidence artifacts captured on 2025-11-14 to validate the quickstart configuration and document audit-ready supporting files.

**Evidence artifacts**
- Screenshot stored externally.
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | Stored externally | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |
