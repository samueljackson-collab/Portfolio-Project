# Operations — P02 IAM Hardening Master Factory

Operational runbook for sustaining IAM least privilege, detecting external access, and cleaning unused credentials.

## Rollout
- Use feature branches with `make validate-policies` and `make simulate` gating merges.
- Require Access Analyzer green status and MFA test pass before tagging a release.
- Deploy via automation that logs every IAM change and triggers `reporting.md` pipelines.

## Rollback
- Keep a last-known-good policy bundle; reapply and rerun `make policy-diff` to confirm parity.
- Re-enable MFA enforcement controls and revoke temporary exceptions.
- Trigger Access Analyzer rescans to ensure no residual external access.

## Hygiene and Cleanup
- Schedule weekly unused credential sweeps; disable keys older than policy thresholds and document in `reporting.md`.
- Review cross-account accesses flagged by Access Analyzer; quarantine unexpected principals.
- Rotate automation role credentials with MFA session enforcement.

## Operational Alerts
- Promote observability alerts for Access Analyzer high/medium findings and MFA failures (see `observability.md`).
- Route cleanup job results to incident channels with runbooks attached.
