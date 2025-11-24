# Orchestration Runbook

## Purpose
Document the steps to launch, observe, and triage orchestration runs for the portfolio platform.

## Preconditions
- Terraform infrastructure applied with the `portfolio` namespace available.
- GitHub Actions deploy pipeline succeeded and pushed images to GHCR.
- Access to Grafana and Prometheus endpoints provisioned by the compose stack or Kubernetes install.

## Kick off a deployment
1. Log in to the React console and navigate to **Orchestration**.
2. Choose environment (`dev`, `staging`, `production`) and enter the target version tag from CI.
3. Provide optional kickoff notes (e.g., change ticket, expected blast radius).
4. Submit the form—this calls `POST /orchestration/runs` and begins tracking.

## Monitor progress
- Use the summary tiles for at-a-glance counts.
- Drill into an individual run to review step events as they stream in from the orchestrator.
- Confirm backend health via `/health` or the `portfolio-backend` service in Kubernetes.

## Add checkpoints
- Post structured events with `POST /orchestration/runs/{id}/events` to mark phase gates (bake times, traffic shift, database migrations).
- Transitions to `succeeded`, `failed`, or `cancelled` immediately update the summary API for Grafana panels.

## Troubleshooting
- **Run not progressing:** Inspect orchestrator container logs and OTEL spans from `app='portfolio-orchestrator'`.
- **API failures:** Validate the Kubernetes service endpoints and security groups provisioned by Terraform.
- **Dashboard gaps:** Ensure `observability/otel-collector.yaml` is applied and Prometheus scrape config includes the collector.

## Rollback
1. Record an event with status `cancelled` to freeze the run in the UI.
2. Deploy the prior image tag via the same form, referencing the previous successful `target_version`.
3. Validate health checks before resuming traffic.
