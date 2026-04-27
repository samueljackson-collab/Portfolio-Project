# Operations Checklists and Runbooks (P01, P03, P25)

Use these daily/weekly/monthly routines and deployment procedures across infrastructure (P01), CI/CD (P03), and observability (P25).

## Daily
- [ ] Review overnight alerts; acknowledge and create incident tickets for P1/P2.
- [ ] Check CI pipeline health and queued jobs; rerun failed tests if flaky.
- [ ] Verify ArgoCD sync status for dev/staging/prod; resolve drift immediately.
- [ ] Confirm observability stack is scraping targets and ingesting traces.

## Weekly
- [ ] Patch CI runners and bastion hosts; rotate ephemeral tokens.
- [ ] Run backup restore test for critical data stores (RDS snapshots, S3 bucket versions).
- [ ] Exercise DR drill: fail over NAT gateway AZ or simulate loss of one AZ route table and confirm traffic re-converges.
- [ ] Review deployment frequency and failure rates; adjust rollout policy thresholds if needed.

## Monthly
- [ ] Full disaster recovery rehearsal with documented RTO/RPO results.
- [ ] Patch cadence review: ensure OS and container base images are updated; rebuild golden AMIs/base images.
- [ ] Audit IAM roles, security groups, and ArgoCD RBAC for least-privilege adherence.
- [ ] Capacity planning check using Grafana dashboards (CPU/mem, NAT utilization, database IOPS).

## Alert tiers (P1–P4)
- **P1**: Prod outage or security incident. Page immediately, start incident bridge, and trigger rollback if deployment-related.
- **P2**: User-impacting degradation. Notify on-call and product owner; consider traffic shift to last stable release.
- **P3**: Limited impact or single component impaired. Create ticket, address within business day.
- **P4**: Informational. Track in backlog.

## Start/Stop procedures
- **Start**: bring up observability stack (`docker compose -f common/observability/docker-compose.yml up -d`), then CI services, then app workloads via ArgoCD sync.
- **Stop**: disable ArgoCD auto-sync, drain traffic (set weights to 0 on canary), stop app workloads, then observability services.

## Deployment (blue/green with health gates)
1. Prepare release manifest or Helm values and push to the GitOps repo.
2. Enable Argo Rollouts canary: start at 10% traffic with health checks on error rate and p95 latency.
3. Promote to 50% then 100% only when health gates pass; otherwise automatically rollback to previous ReplicaSet.
4. Validate post-deploy with smoke tests and security checks (bandit/semgrep) before closing the change.

## Rollback steps
- **ArgoCD/Argo Rollouts**: `kubectl argo rollouts undo <rollout>` or revert Git commit triggering the sync.
- **Infrastructure change**: execute `aws cloudformation cancel-update-stack` or redeploy last successful template version.
- **Database migration**: apply corresponding down migration or restore last backup snapshot; document impact window.

## Backup and restore tests
- [ ] Verify automated snapshots exist for RDS and EBS; test restoring to staging weekly.
- [ ] Validate S3 versioning and lifecycle rules; restore a random object monthly.
- [ ] Capture metrics on restore time and data integrity; log in DR register.
