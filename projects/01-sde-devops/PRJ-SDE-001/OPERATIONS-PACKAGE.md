# Operations Package

## Deployment Runbook
1. **Pre-checks:**
   - Confirm Terraform state backend reachable; lock enabled.
   - Validate secrets in AWS Secrets Manager and parameter store values for environment.
   - Ensure change ticket and maintenance window approved.
2. **Plan & Review:**
   - `make lint && make plan ENV=<env>`
   - Peer review plan output and cost delta; obtain go/no-go from service owner.
3. **Apply:**
   - `make apply ENV=<env>` (dev/stage auto; prod requires manual approval).
   - Monitor `terraform apply` for drift; capture plan/apply artifacts.
4. **Smoke Test:**
   - Hit `/healthz` via ALB; run canary script validating DB connectivity and CRUD.
   - Verify CloudWatch alarms stay green for 15 minutes.
5. **Handover:**
   - Update deployment log in `reports/deployments-<date>.md`.
   - Notify stakeholders and on-call with version, change set, and backout steps.

## Rollback Plan
- **Infrastructure:** Revert to previous Terraform state/tag (`terraform apply <previous-plan>` or `terraform state pull` and re-apply). Disable new ECS task definitions and scale down if ALB health drops.
- **Database:** Restore from last automated snapshot; execute integrity checks; reinstate connections after validation.
- **Traffic:** Use ALB target group weight shift or Route53 failover to previous healthy deployment.
- **Criteria:** Rollback if p95 latency > 500ms for 10 minutes, error rate >1%, or DR checks fail.

## On-Call Playbook
- **Alert Intake:** Alerts route to Slack/PagerDuty with runbook link and service owner.
- **Triage Steps:**
  1. Confirm blast radius (ALB 5xx? ECS task crash? RDS connections?).
  2. Capture metrics snapshot (ALB, ECS, RDS, system logs).
  3. Apply mitigation: scale ECS tasks, failover DB if Multi-AZ, or throttle traffic via WAF.
  4. If unresolved in 15 minutes, execute rollback plan.
- **Post-Incident:** File incident report within 24 hours; update runbook and detection rules.

## Change Management
- **Branches:** feature → PR → `main`; protected branch with required checks.
- **Approvals:** Minimum 2 reviewers for infra changes; security sign-off for public exposure changes.
- **Windows:** Prod deploys during approved windows; emergency changes follow expedited but logged path.
- **Audit:** Change logs stored in `reports/` with plan/apply hashes and ticket references.
