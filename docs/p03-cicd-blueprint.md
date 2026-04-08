# P03 CI/CD Blueprint (ArgoCD GitOps)

This blueprint defines the reference pipeline and outcome targets for the portfolio CI/CD system.

## Pipeline stages
1. **Build & Test**
   - Run unit, integration, and security scans (SAST/dependency) in parallel.
   - Artifacts: build outputs, coverage reports, SARIF.
2. **Staged deploy (GitOps)**
   - Promote from `dev` to `staging` via ArgoCD syncs tied to environment branches or Helm value overlays.
   - Require integration smoke tests post-sync before promotion.
3. **Production canary**
   - Argo Rollouts or progressive delivery: start at 10% traffic, then 100% after health/metrics gates.
   - Automated rollback on error rate/latency regression.

## Operational notes
- Source of truth: Git repository manifests/Helm charts. No manual drift.
- Environments: dev → staging → prod with promotion by Git change.
- Security: signed container images and required policy checks before deploy.
- Observability gates: error rate, p95 latency, and saturation metrics are required for rollout decisions.

## Outcome metrics (placeholders until first runs)
- Deployment frequency: target ~50 per week.
- Lead time: reduce from days to hours.
- Change failure rate: reduce by ~87% from baseline.
- MTTR: decrease with automated rollback and playbook execution.

## Evidence to collect
- CI logs for build/test/security stages.
- ArgoCD sync history for dev/staging.
- Canary rollout timeline with metrics screenshot.
- Rollback demonstration and resulting metrics recovery.
