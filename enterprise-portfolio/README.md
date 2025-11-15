# Enterprise Portfolio

The **Enterprise Portfolio** provides a production-ready reference implementation that combines
infrastructure, platform operations, and application delivery patterns. It is organized so that each
project can be deployed independently while still rolling up into a cohesive program of work.

## Repository Layout

| Path | Description |
| ---- | ----------- |
| `STRUCTURE.md` | Canonical view of the expected directory tree. |
| `PROJECTS.md` | Inventory of all 30 deployable projects across the portfolio. |
| `docs/` | Strategic documents covering architecture, business strategy, and roadmap. |
| `projects/` | Individual project implementations grouped by capability area. |
| `scripts/` | Automation entry points for deployment, validation, and health checks. |
| `terraform/` | Reusable Terraform building blocks and environment configurations. |
| `kubernetes/` | Cluster-wide GitOps, service mesh, and application manifests. |
| `monitoring/` | Prometheus, Grafana, and alerting configurations for observability. |

## Getting Started

```bash
# List every deployable project
./scripts/list-projects.sh

# Deploy a single project
./scripts/deploy-project.sh cloud-infrastructure aws-landing-zone

# Deploy all portfolio projects (sequential)
./scripts/deploy-all.sh

# Validate the repository structure and Terraform modules
./scripts/validate-deployment.sh
./scripts/portfolio-validator.py
```

Each project directory includes:

- A `README.md` describing the objective and deployment workflow.
- A `deploy.sh` script that orchestrates Terraform, Kubernetes, and optional Docker components.
- A `validate.sh` script for format and policy checks.
- A starter `terraform/` module and optional `kubernetes/` Kustomize base.

## Program Governance

- **Architecture** – See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the reference view across
  cloud infrastructure, platform operations, and workloads.
- **Strategy** – [`docs/STRATEGY.md`](docs/STRATEGY.md) outlines the business motivations and value
  stream alignment for the initiative.
- **Roadmap** – [`docs/ROADMAP.md`](docs/ROADMAP.md) breaks the delivery into near, mid, and long
  term milestones so the program can be executed iteratively.

## Portfolio Automation

The GitHub Actions workflow defined in [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)
invokes the same scripts provided locally. This ensures developers, CI, and production automation all
execute the identical deployment entry points.

To extend the automation:

1. Add new projects under `projects/<category>/<project-name>` following the existing pattern.
2. Update `PROJECTS.md` so the documentation stays accurate.
3. Run `./scripts/portfolio-validator.py` to confirm the structure is still compliant.
4. Open a pull request and allow the workflow to execute the validation commands automatically.

## Support

Questions or suggestions? Open an issue or start a discussion so that improvements can be triaged and
prioritized alongside the roadmap.
