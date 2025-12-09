# Threat Model

Threats:
- Image supply-chain attacks
- Cluster credentials in CI logs
- Failed rollouts leaving unhealthy pods

Mitigations:
- Trivy scans + signed images
- Masked secrets and OIDC federation
- ArgoCD health checks + automatic rollback
