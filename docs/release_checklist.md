# Release Checklist (Portfolio)

## Pre-release
- [ ] All 25 projects: `make test-all` green (or justified skips).
- [ ] `scripts/portfolio-status.sh` shows ✅ in Code/Doc/Diag/Test/Obs for each.
- [ ] Security: pre-commit hooks pass; no secrets; CI gates green.
- [ ] Dashboards: P25 updated; runbooks link from alert annotations.

## Evidence
- [ ] Demo-day v2 completed; artifacts saved under each `docs/evidence/`.
- [ ] Grafana snapshot for demo latency; Jaeger trace PNG for RAG.

## Cloud Artifacts
- [ ] P01 dev/stg/prod tfvars valid; RDS password via SSM.
- [ ] P05 mesh: two kubecontexts, failover drill recorded.
- [ ] P21 DR drill timestamps saved.

## Sign-off
- [ ] README indexes updated; Wiki.js re-imported.
- [ ] Tag release `vYYYY.MM.DD`; changelog updated.
