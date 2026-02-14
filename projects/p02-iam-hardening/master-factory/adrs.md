# Architecture Decision Records — P02 IAM Hardening Master Factory

1. **Access Analyzer as gate:** All policy changes must pass Access Analyzer simulations in CI/CD and IaC flows before release.
2. **MFA-first posture:** Privileged roles require MFA; automation roles use conditional MFA keys with limited scope.
3. **Deny by default:** Policies default to deny-all with explicit allow lists; wildcards rejected in `make validate-policies`.
4. **Automated cleanup:** Scheduled jobs remove unused credentials; failures block release until resolved.
5. **Diff-driven change control:** `make policy-diff` artifacts are the source of truth for approvals and audits.
6. **Observability integration:** Access Analyzer, MFA events, and cleanup logs stream to dashboards and alerts to prevent silent drift.
