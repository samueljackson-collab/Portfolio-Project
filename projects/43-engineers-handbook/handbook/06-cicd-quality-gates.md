# CI/CD Quality Gates

**Version:** 2.1 | **Owner:** Platform Engineering | **Last Updated:** 2026-01-10

---

## 1. Gate Definitions

Every PR must pass all gates before merge. Gates are not advisory — failures block merge.

| Gate | Tool | Failure Action | Max Runtime |
|------|------|---------------|------------|
| **Format** | `black`, `isort`, `prettier` | Block merge | 30s |
| **Lint** | `ruff`, `eslint` | Block merge | 1 min |
| **Type Check** | `mypy`, `tsc --noEmit` | Block merge | 2 min |
| **Unit Tests** | `pytest`, `jest` | Block merge | 5 min |
| **Coverage** | `pytest-cov` ≥ 80% | Block merge | — |
| **Integration Tests** | `pytest` (Docker deps) | Block merge | 10 min |
| **SAST** | `semgrep`, `bandit` | Block on HIGH+ | 3 min |
| **Dependency Scan** | `pip-audit`, `npm audit` | Block on HIGH+ | 2 min |
| **Container Scan** | `trivy` | Block on CRITICAL | 5 min |
| **IaC Security** | `tfsec`, `checkov` | Block on HIGH+ | 2 min |

---

## 2. Gate Definitions (Machine-Readable)

See [`qa-gates/gate-definitions.yaml`](../qa-gates/gate-definitions.yaml) for the
full machine-readable gate specification consumed by `gate-checker.py`.

---

## 3. Branch Protection Rules

All `main` and `release/*` branches require:

```yaml
# GitHub Branch Protection (via Terraform / Repository Settings)
required_status_checks:
  strict: true
  contexts:
    - "format"
    - "lint"
    - "type-check"
    - "unit-tests"
    - "coverage"
    - "sast"
    - "dependency-scan"
required_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
require_linear_history: true
allow_force_pushes: false
allow_deletions: false
```

---

## 4. Environment Promotion Gates

Before promoting to the next environment, all gates for the target environment must pass:

### Development → Staging

- [ ] All CI gates green
- [ ] Integration tests pass against staging infrastructure
- [ ] No HIGH/CRITICAL security findings
- [ ] Performance tests within 10% of baseline

### Staging → Production

- [ ] All staging gates green
- [ ] QA sign-off (UAT checklist completed)
- [ ] Change Request approved by CAB
- [ ] Rollback procedure tested
- [ ] Monitoring dashboards updated

---

## 5. Gate Bypass Policy

Bypassing a gate is only permitted in:

1. **P1 security incident** requiring emergency hotfix — CISO approval required
2. **Regulatory deadline** — CTO + Legal approval required

Bypasses must be documented in the PR with:
- Reason for bypass
- Risk accepted
- Approver name and timestamp
- Follow-up ticket to address the bypassed issue

**Bypass frequency target:** < 2 per quarter per team.
