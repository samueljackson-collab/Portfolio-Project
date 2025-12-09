# Runbooks

- Deployment rollback: use argocd app rollback <app> <rev>
- Failed sync: check `kubectl describe` on pods, fix manifest, re-sync
- CI failure: re-run pipeline with diagnostics artifact, validate registry connectivity
