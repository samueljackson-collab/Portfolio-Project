# Operations Manual

## Environments
- **Local:** Docker Compose or Make targets.
- **Staging/Prod:** Provisioned via Terraform (`tools/terraform`) or CloudFormation (`tools/cloudformation`).

## Monitoring
- Expose `/health` endpoints for Kubernetes probes.
- Forward structured logs to centralized logging service.
- Configure metrics scraping using Prometheus annotations in the Kubernetes manifests.

## Incident Response
1. Follow runbooks in `docs/runbooks/` to triage issues.
2. Capture metrics snapshots, logs, and timeline.
3. Open a retrospective issue using `.github/ISSUE_TEMPLATE/incident_report.md` (create as needed).

## Maintenance Windows
- Schedule upgrades via STATUS_BOARD updates.
- Run `make security-check` monthly.
