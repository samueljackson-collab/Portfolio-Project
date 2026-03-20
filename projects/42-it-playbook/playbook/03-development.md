# Playbook Phase 3 — Development

**Version**: 2.0
**Owner**: Engineering Lead
**Last Updated**: 2026-01-10
**Review Cycle**: Quarterly

---

## 1. Purpose

This phase defines the development standards, Git workflow, code review requirements, and sprint ceremonies that all engineering teams must follow. Consistency in process reduces defects, speeds reviews, and makes onboarding faster.

---

## 2. Git Workflow

All repositories follow a trunk-based development model with short-lived feature branches.

### Branch Naming Convention

```
<type>/<ticket-id>-<short-description>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `hotfix`

Examples:
```
feat/PRJ-2026-008-shopify-checkout-integration
fix/PRJ-2026-008-cart-session-timeout
hotfix/PRJ-2026-008-payment-gateway-null-ptr
docs/PRJ-2026-008-api-openapi-spec
```

### Branch Lifecycle

```
main (protected)
  │
  ├── feat/PRJ-008-checkout        (< 3 days lifespan)
  │     │
  │     ├── Commit: wip: scaffold checkout API
  │     ├── Commit: feat: implement Stripe webhook handler
  │     └── Commit: test: add checkout integration tests
  │
  └── Pull Request → Code Review → Merge to main → Delete branch
```

**Rules:**
- No direct commits to `main` — enforced by branch protection
- Feature branches live < 3 days; use feature flags for longer-running work
- Hotfix branches may be created from `main` and merged directly with PM approval
- Rebase (not merge) before opening a PR to keep history linear

### Commit Message Format

Follow Conventional Commits:

```
<type>(<scope>): <short summary>

[optional body: what and why, not how]

[optional footer: BREAKING CHANGE, Refs #ticket]
```

Examples:
```
feat(checkout): add Stripe 3DS payment flow

Implements 3D Secure card authentication per PCI-DSS requirement.
Uses Stripe's automatic 3DS trigger — no manual redirect logic needed.

Refs PRJ-2026-008
```

```
fix(cart): resolve session timeout on mobile browsers

Safari's ITP policy was clearing the session cookie prematurely.
Changed cookie SameSite to None with Secure flag.

Refs PRJ-2026-008
BREAKING CHANGE: Requires HTTPS in all environments (including local dev)
```

---

## 3. Pull Request Requirements

Every PR must satisfy all requirements before review is requested.

### PR Checklist (author completes before requesting review)
- [ ] Branch is rebased on latest `main`
- [ ] PR title follows Conventional Commits format
- [ ] PR description answers: What does this change? Why? How was it tested?
- [ ] Linked to the relevant ticket/issue
- [ ] All CI checks passing (build, lint, tests)
- [ ] No TODO comments (use tickets instead)
- [ ] No commented-out code
- [ ] Self-reviewed diff before requesting review
- [ ] Migration scripts included and reversible (if DB changes)
- [ ] Secrets detection scan passed (no credentials in diff)

### PR Size Guidelines

| Size | Lines Changed | Guidance |
|------|--------------|----------|
| XS | < 50 | Ideal — fast review, low risk |
| S | 50–200 | Good — reviewable in one sitting |
| M | 200–500 | Acceptable — split if possible |
| L | 500–1000 | Requires justification in PR description |
| XL | > 1000 | Requires PM + Lead approval; must be split if possible |

---

## 4. Code Review Checklist (25 Checkpoints)

Reviewers must evaluate all 25 checkpoints. A PR cannot be merged with any blocker unresolved.

### Correctness (Blockers)
1. [ ] **Logic is correct**: The code does what the PR description says it does
2. [ ] **Edge cases handled**: Null/empty inputs, boundary values, concurrent requests
3. [ ] **Error handling**: Failures are caught and handled gracefully; no swallowed exceptions
4. [ ] **No regressions**: Existing tests still pass; no previously working functionality broken
5. [ ] **Security**: No injection vulnerabilities (SQL, XSS, command), secrets exposed, or auth bypasses

### Code Quality (Blockers)
6. [ ] **Readability**: Code can be understood without author explanation; variables/functions named clearly
7. [ ] **Single Responsibility**: Functions/classes do one thing; no god objects
8. [ ] **No duplication**: DRY principle followed; no copy-pasted logic
9. [ ] **Dependencies justified**: New packages/libraries are necessary and approved
10. [ ] **No dead code**: Removed code, unused imports, orphaned functions all cleaned up

### Testing (Blockers)
11. [ ] **Tests exist**: New functionality has unit tests; bug fixes have regression tests
12. [ ] **Tests are meaningful**: Tests verify behaviour, not implementation details; no trivial assertions
13. [ ] **Coverage maintained**: Branch coverage does not decrease from baseline
14. [ ] **Mocks are appropriate**: External services are mocked; mocks are realistic

### Performance (Warnings — must be discussed)
15. [ ] **No N+1 queries**: Database queries inside loops have been identified and addressed
16. [ ] **Indexes considered**: New query patterns are supported by existing or new indexes
17. [ ] **Memory efficiency**: No obvious memory leaks; large collections handled with pagination/streaming

### Maintainability (Warnings)
18. [ ] **Documentation**: Public APIs, non-obvious logic, and config options are documented
19. [ ] **Configuration externalised**: No hardcoded URLs, ports, credentials, or environment-specific values
20. [ ] **Logging appropriate**: Key operations logged at correct level (INFO/WARN/ERROR); no PII in logs
21. [ ] **TODOs replaced**: Any TODO in new code has a linked ticket

### Operational Readiness (Warnings)
22. [ ] **Observability**: Metrics, traces, or logs added for new code paths
23. [ ] **Feature flag**: Long-lived features wrapped in a feature flag
24. [ ] **DB migrations**: Migrations are reversible; no breaking schema changes without a migration plan
25. [ ] **Rollback safe**: Change can be reverted without data loss if deployment fails

---

## 5. Definition of Done

A story or feature is Done only when ALL of the following are true:

**Code**
- [ ] All acceptance criteria from the ticket are met
- [ ] Code reviewed and approved by ≥ 1 peer reviewer (≥ 2 for security-sensitive changes)
- [ ] Branch merged to `main` and feature branch deleted

**Testing**
- [ ] Unit tests written for all new logic (≥ 80% branch coverage on changed files)
- [ ] Integration tests updated or created if applicable
- [ ] Manual smoke test completed by developer in staging environment
- [ ] No P1 or P2 defects open against this story

**Documentation**
- [ ] CHANGELOG.md updated
- [ ] API docs updated (if API surface changed)
- [ ] Runbook updated (if operational procedure changed)
- [ ] Architecture diagram updated (if system topology changed)

**Deployment**
- [ ] Feature deployed to staging environment
- [ ] Smoke tests pass in staging
- [ ] Release notes drafted for features going to production

---

## 6. Sprint Ceremony Templates

### Sprint Planning (2 hours for 2-week sprint)

**Agenda:**
1. Review sprint goal proposal from PM (10 min)
2. Capacity check — who is available, who is on leave (5 min)
3. Walk through prioritised backlog items (45 min)
   - Each item: brief description, questions, story point estimation (Planning Poker)
4. Commit to sprint backlog (20 min)
   - Select items that fit capacity at 70% (leave buffer for unplanned work)
5. Assign items to team members (15 min)
6. Define sprint goal statement (10 min)
7. Action items (5 min)

**Sprint Goal Template:**
> "By the end of this sprint, [user/system] will be able to [capability], which demonstrates [business value]."

**Example:** "By the end of Sprint 3, customers will be able to complete a checkout using Stripe 3DS, which demonstrates our core payment pathway is functional."

### Daily Standup (15 min max)

Each team member answers:
1. What did I complete yesterday that contributed to the sprint goal?
2. What will I work on today?
3. What is blocking me (if anything)?

**Parking Lot**: Any discussion that takes > 2 minutes is moved to a separate meeting.

### Sprint Review (1 hour)

1. Sprint goal achievement: Met / Partially Met / Not Met (with explanation)
2. Demo of completed stories (PM and stakeholders present)
3. Review of metrics: velocity, burndown, defect count
4. Stakeholder feedback captured
5. Stories that didn't complete moved back to backlog with explanation

### Sprint Retrospective (1 hour)

Format: Start / Stop / Continue

- **Start**: Things the team should begin doing
- **Stop**: Things causing friction or harm
- **Continue**: Things working well

Each category: 3–5 items max. Vote on top 2 items to action. Assign owner + due date.

---

## 7. Development Phase Outputs

| Output | Owner | Stored In |
|--------|-------|-----------|
| Source code | Developer | Git repository (`main` branch) |
| Unit tests | Developer | `tests/unit/` |
| Integration tests | QA Engineer | `tests/integration/` |
| CHANGELOG.md | Developer | Repository root |
| Updated API docs | Developer | `docs/api/` |
| Sprint velocity data | PM | Project management tool |

**Next Phase**: [04-testing-qa.md](04-testing-qa.md)
