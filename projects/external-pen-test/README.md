# External Pen Test

A small penetration-testing portal that combines a FastAPI + PostgreSQL backend with a React/Vite analyst UI. The stack also includes container builds, Terraform blueprints for AWS, and CI automation.

## Quickstart
1. **Dependencies**: Docker, Docker Compose, Python 3.11, Node 20.
2. **Start stack**:
   ```bash
   cd projects/external-pen-test
   docker-compose up --build
   ```
3. **Use the app**:
   - Backend API: http://localhost:8000 (interactive docs at `/docs`).
   - Frontend: http://localhost:4173.
   - Create a user via `/auth/register`, then authenticate with `/auth/login` to obtain a JWT for protected routes.

## Architecture
- **Backend**: FastAPI service exposing JWT authentication, CRUD for Targets, Findings, and Exploitations, plus a `/scan` endpoint that inserts a simulated finding. Database access is powered by SQLAlchemy and PostgreSQL. Health is reported at `/health` and returns application and DB status.
- **Frontend**: React + Vite single-page app with protected forms for creating targets and findings and triggering the automated scan workflow.
- **Infrastructure**: Dockerfiles for backend/frontend, docker-compose for local orchestration, Terraform for AWS (ECS/EC2 compute, RDS PostgreSQL, S3 + CloudFront for static assets, IAM roles and security groups).
- **CI**: GitHub Actions workflow installing pinned dependencies, running lint/test steps, and building Docker images for both services.

## Health Endpoint
- `GET /health` returns `{ "status": "ok", "database": "ok" }` when the API and database are reachable.
- The endpoint is unauthenticated to simplify monitoring.

## Testing
- **Backend**: `pytest -q` (uses a SQLite override for isolation).
- **Frontend**: `npm test -- --runInBand` (Jest + React Testing Library).

## Environment
- Configure the backend with `DATABASE_URL` and `SECRET_KEY` (and optionally `CORS_ALLOW`).
- Set `VITE_API_URL` for the frontend to point at the deployed API (docker-compose default is `http://localhost:8000`).
