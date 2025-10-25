# Portfolio Platform Explainer

## What We Built
This monorepo delivers an end-to-end portfolio publishing platform. It includes:
- A FastAPI backend delivering curated portfolio project data.
- A React + Vite frontend that renders responsive project tiles and consumes backend APIs.
- Infrastructure-as-code templates (Terraform and CloudFormation) to stand up cloud resources.
- Automated quality, security, and performance guardrails through linting, testing, and CI workflows.
- Operational artifacts—runbooks, monitoring strategy, scripts, and seed data—for day-two operations.

## Why This Approach Works
- **Monorepo Cohesion:** Housing backend, frontend, and infrastructure together enables consistent tooling, simpler dependency management, and atomic changes across the stack.
- **FastAPI + React:** These modern frameworks provide developer velocity, rich typing, and ecosystem support. FastAPI's async model handles concurrent requests efficiently, while Vite accelerates frontend builds and hot-module reloading.
- **Quality Gates:** Mandating Ruff, ESLint, Prettier, pytest, Vitest, and coverage thresholds ensures code health. Security scanners (bandit, npm audit, tfsec, trivy) catch common vulnerabilities before deployment.
- **IaC & Containers:** Terraform/CloudFormation templates guarantee reproducible infrastructure. Docker, Compose, and Kubernetes manifests provide smooth local-to-production parity.
- **Documentation & Automation:** Comprehensive README, runbooks, and scripts lower onboarding friction and standardize operations.

## Alternative Considerations
- **Backend Framework:** Django REST Framework or Flask could be used, but FastAPI's async-first design and Pydantic integration offer performance and typing benefits.
- **Frontend Stack:** Next.js or Remix enable server-side rendering; however, SPA suffices for portfolio workloads and simplifies hosting.
- **IaC Choice:** Pulumi or AWS CDK provide imperative IaC options. Terraform/CloudFormation were selected for their ubiquity and compatibility with multi-cloud strategies.
- **Package Management:** Poetry or pnpm could manage dependencies. Standard pip/requirements and npm align with the expected tooling for most teams and keep onboarding simple.
