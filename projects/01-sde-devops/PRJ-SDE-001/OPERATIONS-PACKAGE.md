# Operations Package

## Deployment Runbook
1. **Pre-checks**
   - Confirm Terraform state backend reachable; lock enabled; provider versions pinned.
   - Validate secrets in AWS Secrets Manager and parameter store; rotate stale entries before deployment.
   - Ensure change ticket and maintenance window approved; freeze windows respected.
   - Verify capacity: ECR repo exists, ALB cert valid, and KMS keys accessible.
2. **Plan & Review**
   - `make lint && make plan ENV=<env>` to run fmt, validate, tflint, tfsec, OPA.
   - Peer review plan output and cost delta; document diffs and approvals in change log.
   - Capture artifacts (plan.json, cost estimate) in `reports/` with timestamp.
3. **Apply**
   - `make apply ENV=<env>` (dev/stage auto; prod requires manual approval and two reviewers).
   - Monitor `terraform apply` for drift; record state version and outputs.
   - Deploy new ECS task definition; shift traffic with canary/weighted target groups.
4. **Smoke Test**
   - Hit `/healthz` via ALB; run canary validating DB connectivity, migrations, and CRUD flows.
   - Verify CloudWatch alarms stay green for 15 minutes; check logs for error spikes.
5. **Handover**
   - Update deployment log in `reports/deployments-<date>.md` with version, owner, and links to artifacts.
   - Notify stakeholders and on-call with change summary and backout steps.

## Rollback Plan
- **Infrastructure:** Revert to previous Terraform state or tag (`terraform state pull` and re-apply pinned version). Disable new ECS task definitions and scale down if ALB health drops.
- **Database:** Restore from last automated snapshot; run integrity checks (checksums, row counts); reinstate connections after validation.
- **Traffic:** Use ALB target group weight shift or Route53 failover to previous healthy deployment.
- **Criteria:** Rollback if p95 latency > 500ms for 10 minutes, error rate >1%, DR checks fail, or security anomaly detected during deploy.

## On-Call Playbook
- **Alert Intake:** Alerts route to Slack/PagerDuty with runbook link and service owner.
- **Triage Steps:**
  1. Confirm blast radius (ALB 5xx? ECS task crash? RDS connections?).
  2. Capture metrics snapshot (ALB, ECS, RDS, system logs) and recent deploy context.
  3. Apply mitigation: scale ECS tasks, failover DB if Multi-AZ, throttle traffic via WAF, or recycle tasks.
  4. If unresolved in 15 minutes, execute rollback plan; open incident bridge.
- **Post-Incident:** File incident report within 24 hours; update runbooks, detection rules, and ADRs if design changes.

## Change Management
- **Branches:** feature → PR → `main`; protected branch with required checks, signed commits, and reviewers per code owner map.
- **Approvals:** Minimum 2 reviewers for infra changes; security sign-off for public exposure or SG/WAF changes.
- **Windows:** Prod deploys during approved windows; emergency changes follow expedited but logged path with post-incident review.
- **Audit:** Change logs stored in `reports/` with plan/apply hashes, ticket references, and links to CI artifacts.

## DR & Backup Operations
- **Backups:** Automated RDS snapshots daily; transaction logs retained per policy; cross-region copy optional.
- **Drills:** Quarterly DR exercise using `TESTING-SUITE.md` scenarios; document RTO/RPO achieved and gaps.
- **Restore Validation:** Run checksum and synthetic transactions; compare metrics against baselines; keep audit log of validations.
