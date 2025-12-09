# Operations Playbook

- Routine tasks: Rotate SVID certs daily, sync policy bundles via CI, and monitor denied flows in Loki dashboards.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'Nodes enroll via SPIRE, Envoy sidecars enforce OPA policies, and traffic allowed only with valid SVIDs and policy decisions.' completes in target environment.
