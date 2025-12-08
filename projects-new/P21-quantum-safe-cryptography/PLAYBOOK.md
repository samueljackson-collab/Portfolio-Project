# Operations Playbook

- Routine tasks: Rotate test certificates weekly, track algorithm deprecations, and capture handshake traces.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'Build openssl image with OQS, run demo server, execute clients negotiating hybrid ciphers and validate latency/compat.' completes in target environment.
