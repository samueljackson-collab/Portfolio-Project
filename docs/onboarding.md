# Developer Onboarding Guide

Welcome to the Portfolio Monorepo! This guide walks through setting up the development environment, running services, executing tests, and troubleshooting common issues.

## Prerequisites
- Docker and Docker Compose
- Python 3.11
- Node.js 20+
- Terraform 1.5+
- AWS CLI (for provisioning environments)
- Make (optional but recommended)

## Initial Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/sams-jackson/portfolio-monorepo.git
   cd portfolio-monorepo
   ```
2. **Bootstrap tooling**
   ```bash
   ./scripts/setup.sh
   ```
   The script installs Python/Node dependencies and configures pre-commit hooks.

## Running the Stack Locally
The fastest way to spin up all services is via Docker Compose:
```bash
make dev
```
This command builds and starts:
- PostgreSQL database
- Backend API on `http://localhost:8000`
- Frontend SPA served from Nginx on `http://localhost:5173`
- Monitoring exporter on `http://localhost:9090`
- Prometheus (`http://localhost:9091`)
- Grafana (`http://localhost:3000`)

To stop containers, run `make stop`.

## Service Development
### Backend
- Activate a virtual environment and install dependencies from `backend/requirements.txt`.
- Run the app locally with `uvicorn app.main:app --reload`.
- Execute tests using `pytest`. The configuration automatically provisions a temporary SQLite database.

### Frontend
- Install dependencies via `npm install` in `frontend/`.
- Start the dev server with `npm run dev` and open the browser to `http://localhost:5173`.
- Update environment variables in `.env` or `.env.local` for API URLs.

### Infrastructure
- Copy `infra/environments/dev/terraform.tfvars` to a workspace-specific file.
- Run `terraform init` and `terraform plan` to preview changes.
- Ensure AWS credentials are configured via `aws configure` or environment variables.

### Monitoring
- Install Python dependencies via `pip install -r monitoring/requirements.txt`.
- Run exporter locally with `uvicorn app.main:app --port 9090`.
- Import `monitoring/grafana/dashboards/app-metrics.json` into Grafana to view metrics.

## Testing
- `make tests` – backend unit/integration suite.
- `frontend`: run `npm run test` (vitest) for component coverage.
- `e2e-tests/tests/test_api_flows.py`: run API smoke tests using pytest.
- `e2e-tests/k6`: execute load scenarios via `k6 run scenarios.js`.

## Troubleshooting
- **Docker compose fails to start**: ensure ports 5432, 8000, 5173, 9090, 9091, and 3000 are free.
- **Backend cannot connect to database**: verify environment variable `DATABASE_URL` and confirm PostgreSQL container health.
- **Frontend displays network errors**: update `VITE_API_BASE_URL` to match backend host and port.
- **Terraform state lock issues**: release the lock via AWS DynamoDB console or `terraform force-unlock`.
- **Grafana login**: default credentials `admin/admin`; change password on first login.

## Support
For assistance, open a GitHub issue or email `hello@samsjackson.dev`. Welcome aboard!
