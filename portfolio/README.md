# Portfolio Monorepo

This monorepo packages a reference implementation for a full-stack portfolio platform. The project demonstrates a production-minded toolchain that spans API, web frontend, infrastructure-as-code, observability, security gates, and operational runbooks.

## What's Inside

- **Backend** – FastAPI 3.11 service with async SQLAlchemy, JWT auth, Alembic migrations, and pytest coverage targets.
- **Frontend** – React 18 + Vite + TypeScript application styled with Tailwind CSS and configured for production Nginx delivery.
- **Infrastructure** – Terraform VPC module, Helm deployment skeleton, Docker Compose developer stack, and container images.
- **Quality & Security** – Ruff, Black, isort, Bandit, ESLint, Prettier, tfsec, tflint, Trivy, and npm audit wired through CI and Make targets.
- **Observability** – Prometheus, Grafana, and Loki placeholders including starter dashboard JSON templates.
- **Runbooks & Docs** – Daily/weekly/incident playbooks, architecture/security briefs, roadmap, and migration status board.
- **Automation** – Bootstrap script, research agent scaffold, and developer productivity helpers.

## Getting Started

1. **Install tooling**
   - Python 3.11
   - Node.js 20+
   - Docker & Docker Compose
   - Terraform 1.6+
2. **Clone and bootstrap**
   ```bash
   git clone <repo-url>
   cd portfolio
   python tools/bootstrap.py --check
   ```
3. **Start the developer stack**
   ```bash
   make dev
   ```
   The API is available at `http://localhost:8000`, and the frontend is served at `http://localhost:5173` via Nginx.
4. **Run tests and linters**
   ```bash
   make test
   make fmt
   ```
5. **Build artifacts**
   ```bash
   make build
   ```

## Environment Configuration

Copy the provided examples into `.env` files to customize secrets for local development:

- `backend/.env.example`
- `frontend/.env.example`
- `compose/.env.example`
- `infra/.env.example`

## Project Conventions

- Follow [CONTRIBUTING.md](./CONTRIBUTING.md) for branching, commit messages, and review workflow.
- Respect formatting via `ruff`, `black`, `isort`, `eslint`, and `prettier`.
- Ensure backend coverage remains above 80% (enforced via `pytest.ini`).

## Make Targets

| Target     | Description |
|------------|-------------|
| `make dev` | Start the docker-compose developer stack (alias for `make up`). |
| `make up`  | Launch backend, frontend, database, and observability services. |
| `make down`| Tear down the Compose stack and remove volumes. |
| `make test`| Run backend unit/integration tests with coverage and frontend type checks. |
| `make fmt` | Apply formatters and linters across backend, frontend, and IaC. |
| `make build`| Build frontend assets and container images for backend and frontend. |

## Documentation Map

- [Architecture](./docs/architecture.md)
- [Security](./docs/security.md)
- [Roadmap](./ROADMAP.md)
- [Status Board](./STATUS_BOARD.md)
- [Runbooks](./docs/runbooks)
- [Observability Dashboards](./docs/observability/dashboards)

## Bootstrap Kit

Use `tools/bootstrap.py` to regenerate the starter layout or verify required files. The script is idempotent and can help new contributors stand up a clean tree without referencing external archives.

## Research Automation

Generate lightweight dossiers with `python tools/research_agent.py generate "Topic" --template executive`.
The underlying prompt text is stored in `prompts/.private/ai_instruction_bank.json`, keeping AI-facing instructions
separate from the checked-in Markdown placeholders while still allowing the CLI to load the necessary templates.

## License

This repository is distributed under the [MIT License](./LICENSE).

