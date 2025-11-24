# Runbook: Redeploy Test Runner
1. Confirm failing pods via `kubectl -n api-testing get pods`.
2. Delete failing pod to trigger restart.
3. If image outdated, update tag in `k8s/runner.yaml` and `kubectl apply -f k8s/runner.yaml`.
4. Re-run smoke tests: `kubectl -n api-testing logs job/contract-tests`.
