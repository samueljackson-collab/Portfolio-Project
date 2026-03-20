# Playbook Phase 4 — Testing & QA Gates

**Version**: 2.0
**Owner**: QA Engineering
**Last Updated**: 2026-01-10
**Review Cycle**: Quarterly

---

## 1. Purpose

This phase defines the quality gates, test strategy, sign-off criteria, and defect management process that must be completed before any software is released to production.

---

## 2. Test Strategy Template

### 2.1 Test Pyramid

```
         /\
        /E2E\        (10% of tests — slowest, highest confidence)
       /------\
      / Integr \     (20% of tests — service-to-service contracts)
     /----------\
    /  Unit Tests \   (70% of tests — fast, isolated, per-function)
   /--------------\
```

### 2.2 Coverage Thresholds

| Test Level | Coverage Target | Measurement | Enforcement |
|------------|----------------|-------------|-------------|
| Unit | ≥ 80% line coverage | CI coverage report | Build fails below threshold |
| Unit | ≥ 70% branch coverage | CI coverage report | Warning below 70% |
| Integration | ≥ 60% critical paths | Manual + automated | QA sign-off required |
| E2E | All P0 user journeys | E2E test suite | Staging gate |
| Performance | All NFR baselines | Load test tool | Pre-release gate |
| Security | OWASP Top 10 | DAST scan | Pre-release gate |

### 2.3 Test Environment Strategy

| Environment | Purpose | Data | Refresh Cycle |
|-------------|---------|------|--------------|
| Developer local | Unit + integration debug | Mocked/synthetic | Per-developer |
| CI (ephemeral) | All automated tests | Seeded test data | Per PR |
| Staging | Integration, E2E, UAT | Anonymised prod copy | Weekly |
| Pre-prod | Performance, security, final UAT | Sanitised prod subset | Pre-release |
| Production | Smoke tests post-deploy | Real data | Per deployment |

---

## 3. Quality Gate Definitions

### Gate 1: Unit Test Gate

**Entry criteria**: Feature branch PR opened, CI triggered
**Exit criteria**: All checks pass

| Check | Pass Condition | Owner |
|-------|---------------|-------|
| Build succeeds | `exit code 0` | CI |
| Linter passes | 0 errors (warnings allowed) | CI |
| All unit tests pass | 0 failures, 0 errors | CI |
| Line coverage ≥ 80% | coverage report | CI |
| Branch coverage ≥ 70% | coverage report | CI |
| No new security vulnerabilities | 0 HIGH/CRITICAL in diff | CI (Snyk/Bandit) |
| Secrets scan | 0 detected secrets | CI (detect-secrets) |

**SLA**: Must complete within 10 minutes on CI

### Gate 2: Code Review Gate

**Entry criteria**: Unit Test Gate passed, PR submitted for review
**Exit criteria**: PR approved and merged

| Check | Pass Condition | Owner |
|-------|---------------|-------|
| 25-point review checklist | All blockers resolved | Reviewer |
| PR size | ≤ L (1000 lines) or justified | Reviewer |
| No unresolved review comments | All threads resolved or acknowledged | Author |
| Approval count | ≥ 1 (≥ 2 for security-sensitive) | Reviewer |

**SLA**: First review within 4 business hours; author response within 2 hours

### Gate 3: Integration Test Gate

**Entry criteria**: Code merged to `main`, deployed to staging
**Exit criteria**: All integration tests pass

| Check | Pass Condition | Owner |
|-------|---------------|-------|
| Service-to-service integration tests | 100% pass | CI/QA |
| Contract tests (Pact or equivalent) | 0 contract violations | CI |
| Database migration dry-run | Executes without error | CI |
| API compatibility | No breaking changes vs OpenAPI spec | CI |

**SLA**: Must complete within 30 minutes

### Gate 4: UAT / Functional Gate

**Entry criteria**: Integration tests passed, staging environment stable
**Exit criteria**: Business stakeholder sign-off

| Check | Pass Condition | Owner |
|-------|---------------|-------|
| All acceptance criteria from sprint tickets | Verified by QA | QA Engineer |
| Critical user journeys (P0) | 100% pass in staging | QA Engineer |
| Regression test suite | ≥ 95% pass rate | QA Engineer |
| Exploratory testing session | No P1 defects found | QA Engineer |
| Business stakeholder UAT | Written sign-off received | Business Owner |

**SLA**: UAT window is 3 business days for standard releases

### Gate 5: Performance Gate

**Entry criteria**: Functional Gate passed, load test environment prepared
**Exit criteria**: All NFRs met

| Check | Pass Condition | Owner |
|-------|---------------|-------|
| p50 latency | ≤ NFR target (e.g. < 100ms) | QA/DevOps |
| p99 latency | ≤ NFR target (e.g. < 500ms) | QA/DevOps |
| Error rate under load | < 0.1% at target concurrency | QA/DevOps |
| No regressions vs baseline | < 10% degradation | QA/DevOps |
| Peak concurrency sustained | NFR target for 10 minutes | QA/DevOps |

**SLA**: Performance test run completes within 2 hours; results reviewed same day

### Gate 6: Security Gate

**Entry criteria**: Performance Gate passed
**Exit criteria**: Security team sign-off

| Check | Pass Condition | Owner |
|-------|---------------|-------|
| DAST scan (OWASP ZAP or Burp) | 0 Critical, 0 High findings | Security |
| Dependency CVE scan | 0 Critical, 0 High unfixed | CI + Security |
| Secrets in codebase | 0 detected | CI (detect-secrets) |
| Security review checklist | All items checked | Security |
| Penetration test (major releases) | No critical findings outstanding | External/Internal |

**SLA**: Security review within 3 business days; critical findings block release

---

## 4. Sign-off Criteria Matrix

| Role | Gate 1 | Gate 2 | Gate 3 | Gate 4 | Gate 5 | Gate 6 |
|------|--------|--------|--------|--------|--------|--------|
| Developer | Owner | Author | Reviewer | — | — | — |
| Reviewer/Lead | — | Approver | — | — | — | — |
| QA Engineer | — | — | Owner | Owner | Owner | Reviewer |
| Business Owner | — | — | — | **Sign-off** | — | — |
| Security Team | — | — | — | — | — | **Sign-off** |
| DevOps/Ops | — | — | — | — | **Sign-off** | — |
| PM | Notified | Notified | Notified | Facilitator | Notified | Notified |

---

## 5. Defect Classification and Resolution SLAs

### Severity Classification

| Severity | Definition | Example |
|----------|-----------|---------|
| **P1 — Critical** | Production system down or data loss; no workaround | Payment processing completely fails; database corruption |
| **P2 — High** | Major functionality broken; workaround exists but painful | Checkout available but customer cannot apply discount codes |
| **P3 — Medium** | Functionality degraded; reasonable workaround exists | Product images not loading on Safari mobile |
| **P4 — Low** | Minor issue; cosmetic or edge case | Wrong tooltip text on settings page |

### Resolution SLAs

| Severity | Acknowledge | Resolve (Dev) | Resolve (Production) | Regression Test |
|----------|------------|---------------|---------------------|-----------------|
| P1 | 15 minutes | 2 hours | 4 hours | Same day |
| P2 | 1 hour | 8 hours | Same business day | Within 24 hours |
| P3 | 4 hours | 3 business days | Next release cycle | With fix |
| P4 | 1 business day | Next sprint | Next release cycle | Optional |

### Defect Lifecycle

```
New → Triaged (P1-P4 assigned) → In Progress → Fixed → In Review
                                                              │
                           Closed ← Verified (by QA) ←───────┘
                              │
                           Rejected (not a defect / won't fix)
```

### Defect Template

```markdown
**Title**: [Short description — component: behaviour]
**Severity**: P1 / P2 / P3 / P4
**Reporter**: Name, Date
**Environment**: Staging / Production / Version

**Steps to Reproduce**:
1.
2.
3.

**Expected Result**: What should happen
**Actual Result**: What actually happens
**Screenshots/Logs**: Attach

**Frequency**: Always / Intermittent (N/M times)
**Workaround**: Available? Description?

**Root Cause** (filled by developer):
**Fix Description** (filled by developer):
```

---

## 6. Testing Phase Outputs

| Output | Owner | Stored In |
|--------|-------|-----------|
| Test results (unit/integration) | CI | `reports/test-results/` |
| Coverage report | CI | `reports/coverage/` |
| UAT sign-off document | Business Owner | `docs/signoff/` |
| Defect log | QA Engineer | Project management tool |
| Performance test report | QA/DevOps | `reports/performance/` |
| Security scan report | Security | `docs/security/` |

**Next Phase**: [05-deployment-release.md](05-deployment-release.md)
