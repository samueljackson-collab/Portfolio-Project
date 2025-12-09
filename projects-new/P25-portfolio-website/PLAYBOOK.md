# Operations Playbook

- Routine tasks: Purge CDN cache on content updates, rotate CMS tokens, and monitor uptime/LCP via synthetic checks.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'Content updates pulled from CMS at build time, site built with incremental static regeneration, deployed to CDN with preview links.' completes in target environment.
