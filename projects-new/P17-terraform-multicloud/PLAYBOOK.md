# Operations Playbook

- Routine tasks: Rotate backend credentials, lock state with DynamoDB/Blob locks, and tag all resources consistently.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'Terragrunt wrappers configure backends/workspaces, apply modules to provision VPCs, AKS/EKS clusters, and shared services.' completes in target environment.
