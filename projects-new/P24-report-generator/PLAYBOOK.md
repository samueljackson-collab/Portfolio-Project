# Operations Playbook

- Routine tasks: Rotate signing keys, monitor Celery queue depth, and cache assets for performance.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'Ingest data via API, render templates, generate PDFs, sign with GPG, and distribute via S3/email.' completes in target environment.
