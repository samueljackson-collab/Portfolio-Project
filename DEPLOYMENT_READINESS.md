# Deployment Readiness Report

This guide validates the readiness of the portfolio platform (backend API, frontend, and monitoring stack) for deployment. It captures prerequisites, verification commands, and remediation checks gathered during Phase 1 of the deployment review.

## Prerequisites

1. Clone this repository and install Docker, Docker Compose, Node.js (18+), and Python 3.11.
2. Copy `.env.example` files where provided:
   ```bash
   cd backend
   cp .env.example .env
   ```
3. Configure AWS CLI credentials using a dedicated profile (see the portfolio gap analysis for details) if you plan to exercise the infrastructure provisioning workflows.
4. Ensure the following ports are available locally: `3000` (Grafana / frontend), `8000` (FastAPI backend), `9090` (Prometheus), and `9093` (Alertmanager).

All commands below assume you are executing from the repository root.

## Step 1: Deploy Monitoring Stack (P04)

```bash
cd projects/p04-ops-monitoring
make setup
make run
```

Verify container health:

```bash
make status
```

Reload the Prometheus configuration after edits without restarting containers:

```bash
make reload-prometheus
```

Confirm Grafana can reach Prometheus without embedding credentials in the documentation:

```bash
export GRAFANA_USER=${GRAFANA_USER:-admin}
read -r -s -p "Grafana password: " GRAFANA_PASS && echo
curl -u "$GRAFANA_USER:$GRAFANA_PASS" http://localhost:3000/api/datasources
```

The curl command only prints authentication details after you supply the credentials yourself, avoiding plain-text secrets in scripts or logs.

## Step 2: Start Backend API with Metrics

1. Ensure PostgreSQL is available locally or through Docker.
2. Update `backend/.env` with the actual `DATABASE_URL` and `SECRET_KEY`. Avoid exporting secrets directly in the shell—the `.env` file stays ignored by Git to prevent accidental commits.
3. Install backend dependencies and run the server:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. Validate the `/metrics` endpoint:
   ```bash
   curl http://localhost:8000/metrics | head
   ```

## Step 3: Run Frontend (Optional)

Start the frontend in a separate terminal for better log visibility:

```bash
cd frontend
npm install
npm run dev -- --host
```

Use `Ctrl+C` in the respective terminal to stop each service gracefully.

## Step 4: Smoke Tests & Observability Checks

1. Access Grafana at http://localhost:3000 and import the provisioned dashboards found in `projects/p04-ops-monitoring/config/dashboards/json/` automatically via provisioning.
2. Check Prometheus targets at http://localhost:9090/targets to ensure `prometheus`, `node-exporter`, and `backend-api` are all `UP`.
3. Trigger sample API traffic (e.g., `curl http://localhost:8000/health`) and confirm panels in the “Backend Application Metrics” dashboard update.
4. Review Alertmanager at http://localhost:9093 to ensure the receivers load without configuration errors.

## Expected Outcomes

- CI workflows run tests for pull requests while still permitting diagnostic runs on non-main push events.
- Monitoring stack exposes application metrics through Prometheus and Grafana with reproducible provisioning.
- Secrets remain outside source control via `.env` files and redacted credential usage in documentation.

Document any deviations in `DEPLOYMENT.md` or file an issue referencing this readiness guide.
