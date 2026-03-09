---
name: Bug report
about: Report a reproducible problem to help us improve the portfolio assets
labels: ["bug"]
---

## Summary
Provide a concise, one-sentence description of the problem.

## Impact
Who/what is impacted and how severe is it?
- Severity: (Critical/High/Medium/Low)
- User impact:
- Business impact:

## Environment
- Project/area:
- Branch/commit:
- OS/Browser/Runtime:
- Deployment environment (local/staging/prod):

## Steps to Reproduce
1.
2.
3.

## Expected Behavior
What should happen?

## Actual Behavior
What actually happened? Include error messages or screenshots.

## Logs/Artifacts
Paste logs, stack traces, or attach files/screenshots.

## Possible Root Cause
If you have a hypothesis, add it here.

## Workarounds
Any temporary mitigation?

## Acceptance Criteria
- [ ] Fix verified in affected environment
- [ ] Regression coverage added/updated (if applicable)

---

## Example (completed)

**Summary**
Health check endpoint returns 500 for the AWS Infra Automation project after latest deploy.

**Impact**
- Severity: High
- User impact: External monitors report downtime; uptime badge shows failure.
- Business impact: Demo reliability is reduced during portfolio reviews.

**Environment**
- Project/area: `projects/1-aws-infrastructure-automation` health check
- Branch/commit: `main` @ `33e8c68`
- OS/Browser/Runtime: Ubuntu 22.04, curl 8.5.0
- Deployment environment (local/staging/prod): prod

**Steps to Reproduce**
1. `curl -i https://aws-infra-automation.example.com/healthz`
2. Observe HTTP 500 response.

**Expected Behavior**
Health check returns HTTP 200 and JSON payload `{ "status": "ok" }`.

**Actual Behavior**
HTTP 500 with body `{"error":"DB connection failed"}`.

**Logs/Artifacts**
```
2025-11-12T10:42:33Z ERROR db: connection refused (rds-prod-01)
```

**Possible Root Cause**
Recent DB security group change may be blocking the app tier.

**Workarounds**
Restarting the app task temporarily restores connectivity.

**Acceptance Criteria**
- [ ] Health check returns 200 for 24h with no errors
- [ ] Add a deployment smoke test for `/healthz`
