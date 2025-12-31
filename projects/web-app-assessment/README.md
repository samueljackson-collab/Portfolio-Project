# Web App Assessment

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


A simulated assessment platform with a FastAPI backend, React dashboard, infrastructure as code, and CI automation. The project demonstrates authenticated CRUD over application assets, a deterministic vulnerability scan, and a responsive UI for reviewing results.

## Features
- **FastAPI backend** with JWT-protected CRUD for endpoints, pages, and vulnerability findings.
- **Deterministic scan** via `/scan-page` that applies repeatable rules (HTTP vs HTTPS, debug flags, identifier parameters, token exposure).
- **React frontend** providing login, endpoint-based grouping of pages and findings, scan submission form, and responsive layout with error handling.
- **Dockerized** services with Compose for local development.
- **Terraform** stack for a containerized backend (ECS), PostgreSQL (RDS), static hosting (S3 + CloudFront), and restricted security groups.
- **GitHub Actions CI** to lint, test, and build backend and frontend assets.

## Backend

- Base URL: `http://localhost:8000`
- Auth: `POST /login` with `admin/password` for demo tokens (Authorization: `Bearer <token>` on protected routes).
- CRUD routes: `/endpoints`, `/pages`, `/findings` (GET/POST for demo storage).
- Scan route: `POST /scan-page` with `{ "endpoint_id": <id>, "url": "http://..." }`.
- Health check: `/health`.

The scan engine lives in `app/scanner.py` and returns simulated findings for predictable patterns (plain HTTP, `debug` flags, `id=` parameters, and `token=` query strings). Pages are added to the in-memory store when scanned, and findings are attached to that page entry.

## Frontend

- Vite + React (TypeScript) app located in `frontend/`.
- Reads `VITE_API_URL` (default `http://localhost:8000`).
- Provides:
  - Login form with inline error messages.
  - Dashboard grouping pages and findings by endpoint.
  - Scan form targeting any endpoint.
  - Responsive cards/grid layout and muted loading/error states.

### Running locally with Docker Compose

```bash
cd projects/web-app-assessment
docker compose up --build
```
- Backend available at `http://localhost:8000`
- Frontend available at `http://localhost:3000`

### Manual backend run

```bash
cd projects/web-app-assessment/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Manual frontend run

```bash
cd projects/web-app-assessment/frontend
npm install
npm run dev -- --host
```

## Terraform deployment (AWS)

1. Configure AWS credentials and optionally update `backend_allowed_cidrs` to restrict ingress (defaults to RFC1918 example).
2. Set required variables for container image and roles:
   - `backend_image`
   - `ecs_execution_role_arn`
   - `ecs_task_role_arn`
   - `db_username`
   - `db_password`
3. Initialize and apply:

```bash
cd projects/web-app-assessment/terraform
terraform init
terraform plan -out plan.tfplan -var "backend_image=<account>.dkr.ecr.<region>.amazonaws.com/web-app-assessment:latest" -var "db_username=webuser" -var "db_password=example-pass"
terraform apply plan.tfplan
```

Outputs include the CloudFront domain for the static frontend and the database endpoint for the backend service.

## GitHub Actions CI

The workflow (`.github/workflows/ci-web-app-assessment.yml`) installs dependencies, runs Python tests (`pytest`), executes frontend linting (`npm run lint`), and builds the Vite bundle. It serves as a safeguard to keep application logic, UI, and infrastructure manifests in sync.

## Example usage

1. Login via the frontend with `admin/password`.
2. Select an endpoint (API or UI) and submit a URL such as `http://example.com/app?id=1&debug=true`.
3. The dashboard refreshes with the scanned page and simulated findings showing severity, rule, and timestamp grouped under the endpoint.

## Limitations

- Data stores are in-memory for demo purposes (no persistence without external backing services).
- JWT secret and credentials are static; replace them before production use.
- The scan is intentionally simplified to deterministic string checks and does not replace a real DAST engine.
