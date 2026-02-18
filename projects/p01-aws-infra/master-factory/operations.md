# Operations

## Deployment Runbook
1. `make lint && make test`.
2. `make plan` (Terraform) and capture plan output.
3. Change advisory approval.
4. `make apply` targeting env (`ENV=dev|prod`).
5. Verify ALB health checks and RDS connectivity via `scripts/verify_rds.sh`.

## Change Management
- Use GitHub PR templates with checklist for Config/GuardDuty outputs.
- Tag releases `p01-vX.Y.Z` and upload plan/apply logs to `artifacts/releases/`.

## Incident Response
- Primary alarms: ALB 5xx rate, RDS latency, Route53 health check failure, DR drill failure.
- On alarm: engage on-call, run `scripts/dr-drill.sh --verify-only`, collect CloudWatch metrics, and document in incident record.

## Backup & Restore
- Daily RDS snapshots with 7-day retention.
- Weekly cross-region snapshot copy; test restore monthly using `scripts/restore_rds.sh` (dry-run available).

## DR Drills
- Quarterly failover to secondary region with documented RPO/RTO.
- Capture evidence: Route53 status, RDS promotion time, app smoke test results.
