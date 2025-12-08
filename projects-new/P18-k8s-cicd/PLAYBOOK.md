# Operations Playbook

- Routine tasks: Rotate registry credentials, prune old images, and monitor ArgoCD health sync status.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'CI builds container, runs tests and Trivy, pushes to registry, ArgoCD watches manifests and syncs to cluster.' completes in target environment.
