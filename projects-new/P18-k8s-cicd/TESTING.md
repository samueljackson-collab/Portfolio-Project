# Testing

Automated commands:
- make lint
- make test
- make kind-e2e

Manual validation:
- Verify Pod creation succeeded in Kind cluster
- Confirm ArgoCD application sync status is healthy
- Check that image scan reports no critical vulnerabilities in Trivy output
- Validate GitOps rollback can be triggered and completes successfully
