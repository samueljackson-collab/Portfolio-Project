# Playbook Phase 5 — Deployment & Release

**Version**: 2.1 | **Owner**: DevOps / Release Engineering | **Last Updated**: 2026-01-10

---

## 1. Purpose

This phase governs the controlled promotion of tested software from staging to production,
ensuring zero-downtime deployments, documented rollback procedures, and stakeholder communication.

---

## 2. Pre-Deployment Checklist

### 2.1 Technical Gates (all must pass before production deploy)

- [ ] All CI/CD pipeline stages green (lint, test, security scan, build)
- [ ] Staging environment validation passed (smoke tests + integration tests)
- [ ] Performance testing completed — no regression > 10% on p95 latency
- [ ] Security review sign-off (SAST, DAST, dependency scan clean)
- [ ] Database migration scripts tested on staging with production-size data
- [ ] Runbook reviewed and updated by deploying engineer
- [ ] Rollback procedure tested in staging
- [ ] Monitoring alerts and dashboards updated for new feature

### 2.2 Business Gates

- [ ] Change Request (CR) approved by Change Advisory Board (CAB)
- [ ] Release notes prepared (internal + customer-facing if applicable)
- [ ] Customer communication sent (if user-facing change)
- [ ] Business owner sign-off on UAT results

---

## 3. Deployment Strategies

| Strategy | Use Case | Downtime | Rollback Speed |
|----------|---------|---------|----------------|
| **Blue/Green** | Stateless apps, zero-downtime critical | None | Instant (DNS/LB swap) |
| **Canary** | High-traffic, risk mitigation | None | Minutes (traffic shift) |
| **Rolling** | Kubernetes deployments | None | Minutes (previous tag) |
| **Feature Flags** | Gradual feature rollout | None | Instant (flag toggle) |
| **Maintenance Window** | DB schema changes, monoliths | Scheduled | Manual restore |

---

## 4. Deployment Runbook Template

```bash
# 1. Notify team — deployment starting
echo "Deploy started: $(date -u)" | tee -a /var/log/deployments.log

# 2. Tag release
git tag -a v$(VERSION) -m "Release v$(VERSION)" && git push origin v$(VERSION)

# 3. Run deployment (Kubernetes example)
kubectl set image deployment/$(APP_NAME) $(APP_NAME)=$(IMAGE):$(VERSION) \
  --namespace=$(NAMESPACE)

# 4. Monitor rollout
kubectl rollout status deployment/$(APP_NAME) --namespace=$(NAMESPACE) \
  --timeout=300s

# 5. Smoke test
curl -sf https://$(APP_URL)/health || { echo "Health check FAILED"; exit 1; }

# 6. Confirm success
echo "Deploy complete: $(date -u) — v$(VERSION)" | tee -a /var/log/deployments.log
```

---

## 5. Rollback Procedure

```bash
# Kubernetes: roll back to previous version
kubectl rollout undo deployment/$(APP_NAME) --namespace=$(NAMESPACE)
kubectl rollout status deployment/$(APP_NAME) --namespace=$(NAMESPACE)

# Database rollback (if migration applied)
# Run the down-migration script
python manage.py db downgrade --target $(PREVIOUS_MIGRATION_ID)

# Feature flag rollback (LaunchDarkly / Unleash)
# Toggle flag off via API or console — no deploy needed
```

---

## 6. Post-Deployment Checklist

- [ ] Health check endpoint returns 200 across all pods/instances
- [ ] Key business metrics not degraded (orders, logins, API calls)
- [ ] Error rate unchanged (< 0.1% increase)
- [ ] Latency within SLA (p99 < target)
- [ ] Monitoring alerts have NOT fired
- [ ] Release notes published in internal wiki
- [ ] Change Request (CR) closed with deployment evidence
- [ ] Team notified (Slack #deployments channel)

---

## 7. Release Communication Template

```
Subject: [DEPLOYED] APP_NAME v{VERSION} — {DATE}

Deployed: {APP_NAME} v{VERSION} to production at {TIME} UTC.

Changes:
  - {Feature/fix 1}
  - {Feature/fix 2}

Status: ✅ Successful — health checks passing, no alerts fired.

Rollback plan: Available — estimated 5 minutes if required.
CR Ref: CR-{NUMBER}
Runbook: {WIKI LINK}
```
