# Project 3: Kubernetes CI/CD Pipeline Assets

Evidence artifacts for the GitOps-ready CI/CD pipeline. All screenshots/logs are sanitized and use placeholder project names, registries, and cluster identifiers.

## Contents
- **screenshots/** — GitHub Actions workflow, Argo CD sync, and rollout status captures (SVG placeholders).
- **logs/** — Pipeline run summaries and Argo CD sync logs (sanitized).

## Evidence Index
- Screenshots:
  - `screenshots/project-3-cicd_pipeline_01_20251110.svg` — GitHub Actions workflow summary.
  - `screenshots/project-3-cicd_pipeline_02_20251110.svg` — Argo CD sync health view.
  - `screenshots/project-3-cicd_pipeline_03_20251110.svg` — Argo Rollouts canary status.
- Logs:
  - `logs/github-actions-run.txt` — CI stages with lint/test/scan/build.
  - `logs/argocd-sync.txt` — GitOps sync summary and rollout promotion.

## Sanitization Notes
- Registry URLs and cluster IDs are placeholders.
- Build artifacts and secrets are redacted.
- Timestamps are preserved for sequencing, not for real-world correlation.

## References
- [Project README](../README.md)
- [SCREENSHOT_GUIDE.md](../../../SCREENSHOT_GUIDE.md)
