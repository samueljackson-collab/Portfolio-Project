# P02 · IAM Security Hardening — Incident Playbook

This playbook outlines response procedures for common IAM-focused security events.

## P1 — Compromised Privileged Credentials
1. Trigger PagerDuty (`SEC-IAM-Compromise` service) and assemble incident bridge.
2. Revoke active sessions via `aws iam list-roles --query` + `aws sts revoke-session` for affected principals.
3. Disable access keys and deactivate the compromised account in Identity Center.
4. Rotate break-glass credentials and verify CloudTrail captures the action.
5. Run forensic queries in CloudTrail Lake for the affected timeframe.
6. Document impact, remediation, and lessons learned in `SEC-INC-*`.

## P1 — Unauthorized Policy Change Detected
1. Lock IAM changes by denying `iam:*` through an SCP scoped to the affected account.
2. Use `git diff` against `projects/p02-iam-hardening/policies/` to determine authorised baseline.
3. Restore known-good policy via Terraform apply.
4. Investigate CloudTrail events for the caller identity; disable or quarantine as needed.
5. Remove temporary SCP block once verified; note all actions in the incident log.

## P2 — Excessive Failed Login Attempts
1. Validate GuardDuty findings and confirm the source IP(s).
2. Temporarily require re-registration of MFA for the affected user or role session.
3. Block offending IP ranges at the perimeter firewall (AWS WAF or security appliance).
4. Notify the user via secure channel; reset credentials if suspicious activity confirmed.
5. Track incident metrics to confirm trend returns to baseline within 24 hours.

## P2 — Dormant Access Key Detected
1. Run automation script `projects/p02-iam-hardening/scripts/disable-stale-key.sh <user>`.
2. Notify resource owner to confirm whether key is still required.
3. If no response within 48 hours, delete the key and update audit trail.
4. Update IAM usage dashboard to reflect closure.

## P3 — Policy Validation Pipeline Failure
1. Inspect the latest CI run in GitHub Actions (`IAM Policy Check` workflow).
2. Run `make iam-test` locally to reproduce; capture failing policy or Rego test.
3. Open defect ticket referencing commit hash and affected policy.
4. Block merges via branch protection until tests are passing.

## Communication Templates
- **Initial Alert:** "Potential IAM security event detected. Investigating root cause; next update in 15 minutes."
- **Containment Complete:** "Containment applied (actions listed). Monitoring for additional activity."
- **Closure:** "Incident resolved. Root cause: <summary>. Follow-up actions: <list>."

Store completed incident reports under `documentation/security/incidents/<year>/`.
