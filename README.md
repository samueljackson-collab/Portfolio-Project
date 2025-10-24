# Portfolio Monorepo

This repository contains a production-style monorepo that powers a complete systems engineering portfolio. It demonstrates full-stack delivery across backend, frontend, infrastructure, testing, and observability concerns.

## 🚀 Quick Start

```bash
# bootstrap dev tools
./setup.sh

# run full stack locally
make dev

# run quality gates
make ci
```

## 🧱 Repository Layout

| Path | Description |
| --- | --- |
| `backend/` | FastAPI service with PostgreSQL persistence and JWT authentication |
| `frontend/` | Vite + React + Tailwind SPA that consumes the backend APIs |
| `e2e-tests/` | Postman, k6, and ZAP automation suites for end-to-end validation |
| `infra/` | Terraform infrastructure modules and environment stacks |
| `monitoring/` | Metrics exporter and Grafana dashboards |
| `docs/` | Architecture and operational documentation |
| `.github/` | CI/CD automation powered by GitHub Actions |
| `tools/`, `scripts/` | Automation utilities and packaging helpers |
| `tasks/`, `data/`, `prompts/`, `SPEC/` | Planning, metadata, and AI enablement assets |

## 🔁 Development Lifecycle

1. Provision infrastructure with Terraform modules under `infra/`.
2. Build and run backend/frontend services via Docker Compose.
3. Execute automated tests (unit, integration, e2e) through `make ci`.
4. Monitor health using the Prometheus exporter and Grafana dashboards in `monitoring/`.
5. Deploy using the GitHub Actions pipelines defined in `.github/workflows/`.

## 🧪 Testing Strategy

The repository follows a testing pyramid:

- **Unit tests**: FastAPI and React units (`pytest`, `vitest`).
- **Integration tests**: API workflow coverage and component interplay.
- **End-to-end tests**: Postman flows, k6 load simulations, and ZAP security scans.

Refer to [`docs/testing.md`](docs/testing.md) for detail on tooling, coverage targets, and execution commands.

## 🛡️ Security & Compliance

- Secrets managed through environment variables with `.env.example` templates.
- Automated dependency scanning (pip-audit, npm audit, Snyk) and infrastructure scanning (tfsec, Checkov).
- JWT-based authentication with refresh token support for session continuity.

## 📈 Observability

The monitoring service exposes Prometheus metrics that feed Grafana dashboards bundled under `monitoring/grafana/dashboards/`. Alerting rules and runbooks are documented in [`docs/deployment.md`](docs/deployment.md).

## 📊 Advanced Reporting

Portfolio-wide analytics can be generated with the advanced report generator under `tools/reporting/`. It produces PDF, HTML, Markdown, JSON, and Excel outputs enriched with AI-driven predictions and interactive Plotly dashboards:

```python
import asyncio
from tools.reporting import AdvancedReportGenerator

async def main():
    generator = AdvancedReportGenerator()
    results = await generator.generate_portfolio_report(
        report_type="executive", output_formats=("html", "pdf", "json")
    )
    print(results)

asyncio.run(main())
```

Generated artefacts are written to the `reports/` directory alongside accompanying radar and trend visualisations when Plotly is available.

## 📬 Support

Open an issue using the templates under `.github/ISSUE_TEMPLATE/` or reach out via the contact details in the project documentation. Contributions are welcome—see [`CONTRIBUTING.md`](CONTRIBUTING.md).

