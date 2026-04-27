# AI Agent Portfolio

This portfolio packages a cohesive set of JSON-driven agents, Terraform usage examples, dashboard configuration, and Wiki.js import specs to accelerate AI-powered CI/CD and documentation workflows.

## Contents
- `build_agent.json` — Build automation template with platform-aware scripts.
- `deploy_agent.json` — Deployment orchestrator template with configurable strategies.
- `test_agent.json` — Testing automation template spanning unit through E2E.
- `document_agent.json` — Documentation generation template with flexible outputs.
- `terraform_examples.md` — Terraform snippets demonstrating agent invocation patterns.
- `portfolio_dashboard.json` — Landing/dashboard configuration for portfolio status and quick-start guidance.
- `wikijs_import_spec.json` — Import rules for Wiki.js to publish portfolio docs.
- `codex_blueprint.json` — Master blueprint describing the ecosystem components and standards.

## Usage
1. Customize each agent JSON template to align with your toolchain and compliance requirements.
2. Apply the Terraform examples to integrate the agents into your provisioning pipelines.
3. Surface portfolio status by feeding `portfolio_dashboard.json` into your dashboard renderer.
4. Import `wikijs_import_spec.json` into Wiki.js to bootstrap documentation.
5. Reference `codex_blueprint.json` for governance, workflow phases, and integration expectations.

## Notes
- Keep parameter defaults conservative for production environments.
- Align deployment strategies with your rollback and health verification policies.
- Enable change tracking in Wiki.js imports to maintain auditability.
