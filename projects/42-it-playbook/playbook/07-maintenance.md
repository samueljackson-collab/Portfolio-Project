# Playbook Phase 7 — Maintenance & Support

**Version**: 2.1 | **Owner**: IT Operations | **Last Updated**: 2026-01-10

---

## 1. Purpose

This phase covers ongoing system health: patch management, capacity planning, performance
tuning, dependency updates, and technical debt reduction.

---

## 2. Patch Management

### Patch Classification and SLA

| Severity | Description | Apply Within |
|----------|-------------|-------------|
| **Critical** (CVSS ≥ 9.0) | Active exploit or RCE | 24 hours (emergency CAB) |
| **High** (CVSS 7.0–8.9) | Likely exploitable | 7 days |
| **Medium** (CVSS 4.0–6.9) | Limited exposure | 30 days |
| **Low** (CVSS < 4.0) | Minimal risk | 90 days |

### Patch Process

```
1. Vulnerability identified (scanner: Qualys, Trivy, Dependabot)
2. Assess CVSS score + exploitability in our environment
3. Test patch in dev/staging environment
4. Raise Change Request (CR) with patch details
5. Deploy to production during approved window
6. Verify patch applied: package manager / kubectl image inspect
7. Close CR with evidence (scan report showing resolved)
8. Record in patch register (CMDB)
```

---

## 3. Capacity Planning

### Quarterly Review Checklist

- [ ] Review 90-day trend for CPU, memory, storage, network per service
- [ ] Project growth for next 6 months (use 20th-percentile trend)
- [ ] Identify services approaching > 70% resource utilisation
- [ ] Confirm auto-scaling policies set correctly
- [ ] Review cost optimization opportunities (right-sizing)
- [ ] Update capacity plan document with next 6-month projections

### Scaling Decision Matrix

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU average > 70% for 7 days | Sustained load | Scale up or optimise |
| Memory > 80% for 7 days | Memory pressure | Scale up or profile for leaks |
| Storage > 75% | Disk pressure | Expand or archive data |
| DB connections > 80% of pool | Connection pressure | Increase pool or add read replica |
| Queue depth trending up | Throughput limit | Add consumers or scale horizontally |

---

## 4. Dependency Management

### Monthly Dependency Review

```bash
# Python — check outdated packages
pip list --outdated

# Node.js — check vulnerabilities
npm audit
npm outdated

# Container images — check for vulnerabilities
trivy image $(IMAGE_NAME):latest

# Terraform providers — check for updates
terraform providers lock -upgrade
```

### Dependency Update Policy

- **Major version updates**: Require test plan, regression suite, and staged rollout
- **Minor/patch updates**: Can be applied in routine maintenance window after testing
- **Security patches**: Follow patch SLA above regardless of semver

---

## 5. Technical Debt Register

Maintain a living document tracking known technical debt items:

| ID | Description | Impact | Effort | Priority | Owner | Target Quarter |
|----|-------------|--------|--------|----------|-------|---------------|
| TD-001 | Replace deprecated API client v1 | Medium | 2 days | P2 | Dev Team | Q1 2026 |
| TD-002 | Migrate from MySQL 5.7 → 8.0 | High | 5 days | P1 | DBA | Q1 2026 |
| TD-003 | Remove hardcoded config values | Low | 1 day | P3 | Dev Team | Q2 2026 |

---

## 6. Backup Validation

### Monthly Backup Test Procedure

```bash
# Restore latest backup to isolated test environment
aws s3 cp s3://backups/latest/db_dump.sql.gz /tmp/

# Restore to test DB
gunzip -c /tmp/db_dump.sql.gz | mysql -h test-db -u restore_user -p test_restore_db

# Validate row counts match production
mysql -h test-db -e "SELECT table_name, table_rows FROM information_schema.tables
  WHERE table_schema = 'test_restore_db' ORDER BY table_rows DESC LIMIT 10;"

# Document results in backup register
echo "$(date -u) | Backup test PASSED | Record count: $(COUNT)" >> backup_test_log.txt
```
