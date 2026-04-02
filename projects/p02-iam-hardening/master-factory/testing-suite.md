# Testing Suite — P02 IAM Hardening Master Factory

Use the existing Make targets to validate IAM changes end-to-end. Align every run to least privilege, external-access detection, and unused credential cleanup.

## Workflow
1. `make setup` — Install IAM tooling (linters, Access Analyzer helpers, MFA test harnesses).
2. `make validate-policies` — Static validation for least-privilege structure, including deny-by-default checks.
3. `make policy-diff` — Compare generated policies against deployed state; flag new external principals or broader actions.
4. `make simulate` — Run Access Analyzer simulations and MFA enforcement tests against staged policies.
5. `make test` — Execute integration tests for cleanup jobs (unused keys/roles), policy attachments, and analyzer alert routing.

## Test Scenarios
- **Least privilege enforcement:** Assert no wildcards remain after diff; simulate should return zero high-risk findings.
- **External access detection:** Ensure Access Analyzer reports fail CI when new cross-account or public access appears.
- **MFA enforcement:** Validate that privileged roles demand MFA sessions and automation roles use conditional keys.
- **Unused credential cleanup:** Confirm scheduled jobs identify and disable aged keys and unused roles, with reports emitted.

## Evidence Collection
- Archive `make policy-diff` outputs for auditing.
- Export Access Analyzer findings and MFA test logs to observability dashboards (see `observability.md`).
- Include failing scenarios in `reporting.md` to track MTTR for IAM hygiene.
