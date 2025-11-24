# Multi-region runtime runbook

## Symptoms
- Alerts: `PortfolioAPIDown`, `MultiRegionDrift`, or sustained error rate spikes on the operator console.
- Region rollups show available replicas lagging desired replicas for more than 10 minutes.

## Diagnosis steps
1. Check the operator console (`/operator-console`) to confirm which region is unhealthy and the deployment version.
2. Inspect Prometheus alerts and Grafana dashboard (`operations/observability/grafana-multi-region.json`) for request latency and replica counts.
3. Verify Argo CD application status for the affected overlay:
   ```bash
   kubectl -n argocd get applications portfolio-multi-region
   ```
4. Confirm that artifact replication is healthy by checking S3 replication metrics in CloudWatch and DynamoDB replica lag for `service_config`.

## Remediation
- If a rollout is stuck, pause auto-sync for the region and redeploy the last known good image tag.
- Scale the deployment temporarily:
  ```bash
  kubectl -n portfolio scale deployment/use1-portfolio-api --replicas=4
  ```
- If primary region is down, promote the secondary overlay by pointing ingress/DNS to the `eu-west-1` service and validate health probes.
- After recovery, re-enable GitOps sync and update the deployment record via `POST /deployments` to reflect the restored version.
