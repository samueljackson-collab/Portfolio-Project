# Security — P02 IAM Hardening Master Factory

Security guardrails concentrate on enforcing least privilege, eliminating external-access drift, and ensuring MFA-first operations.

## Controls
- Mandatory Access Analyzer scans on every `make simulate` and pre-apply IaC run.
- MFA required for privileged roles; session policies enforce MFA for console and CLI access.
- Deny statements for wildcard actions and unknown principals by default.
- Automated disablement of unused credentials with alerting.

## Reviews
- PR checklist ties to `make validate-policies` and `make policy-diff` outputs.
- CI gates block merges when Access Analyzer reports high/medium findings or MFA enforcement fails.
- Quarterly control review to refresh policy baselines and cleanup thresholds.

## Exceptions
- Break-glass roles documented with time-bounded approvals; Access Analyzer rescans post-use.
- Exceptions must include remediation plans and test evidence stored in `reporting.md`.
