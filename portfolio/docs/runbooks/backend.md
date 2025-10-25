# Backend Runbook

## Service Summary
- **Component:** FastAPI service
- **Entry Point:** `uvicorn projects.backend.app.main:app`
- **Health Check:** `GET /health`

## On-Call Checklist
1. Verify `/health` returns HTTP 200.
2. Review logs in centralized logging system for errors.
3. Run `make test-backend` to ensure regression coverage when patching.

## Common Issues
| Symptom | Action |
|---------|--------|
| 5xx responses | Check configuration in `projects/backend/app/core/config.py`. Validate environment variables. |
| Slow responses | Profile endpoints with `uvicorn --reload --log-level debug` and inspect external dependencies. |
| CI failures | Run `ruff check` and `pytest` locally to reproduce. |

## Deployment Steps
1. Update version in `projects/backend/pyproject.toml` if applicable.
2. Build Docker image: `docker build -t portfolio-backend:latest projects/backend`.
3. Deploy via Terraform or Kubernetes manifests in `projects/backend/infra/k8s`.
