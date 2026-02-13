# Portfolio Monorepo

This repository houses an end-to-end portfolio platform that showcases a full-stack reference implementation spanning infrastructure-as-code, backend services, frontend applications, and operational tooling. It is designed as a launchpad for demonstrating engineering practices, quality gates, and documentation standards in one cohesive workspace.

## Highlights
- **Backend**: FastAPI with async SQLAlchemy and Alembic migrations, fully tested with pytest/httpx.
- **Frontend**: React 18 + Vite + TypeScript (strict) with Tailwind CSS, Axios-powered API client, and health-check integration.
- **Infrastructure**: Terraform 1.6+ configuration targeting AWS with remote state (S3 + DynamoDB), modular VPC, and container stack via Docker Compose.
- **Security & Quality**: Automated linting, formatting, vulnerability scanning, and policy checks across Python, JavaScript, Docker, and Terraform ecosystems.
- **Operations**: Runbooks, observability placeholders, and CI/CD pipelines orchestrated through GitHub Actions and Make targets.

## Repository Layout
```
portfolio/
├── projects/
│   ├── backend/       # FastAPI service
│   ├── frontend/      # React + Vite application
│   └── infra/         # Terraform and deployment assets
├── docs/              # Architecture notes, runbooks, observability assets
├── scripts/           # Helper automation scripts
├── tasks/             # Task tracking and backlog artifacts
├── tools/             # Supporting tooling configs and templates
├── SPEC/              # Product and engineering specifications
├── .github/           # CI/CD workflows and issue templates
└── ...                # Repository-wide configs and metadata
```

## Getting Started
1. **Clone** the repository and install prerequisites: Docker, Docker Compose, Python 3.11, Node.js 18+, Terraform 1.6+.
2. **Install Python dependencies**:
   ```bash
   make setup-py
   ```
3. **Install Node dependencies**:
   ```bash
   (cd projects/frontend && npm install)
   ```
4. **Launch the stack**:
   ```bash
   make up
   ```
   Visit `http://localhost:5173` for the frontend and `http://localhost:8000/docs` for the backend API docs.

## Testing & Quality
- `make test` runs backend unit/integration tests with coverage and frontend unit checks.
- `make lint` executes ruff, black, isort, bandit, eslint, prettier, tflint, tfsec, and npm audit (stubbed).
- `make fmt` applies Python, TypeScript, and Terraform formatters.

## Documentation
Key documentation is organized under `docs/`:
- `docs/architecture.md`: High-level system overview.
- `docs/runbooks/`: Daily, weekly, monthly operational procedures and restore guides.
- `docs/observability/`: JSON dashboard placeholders.

## Contributing
Please read `CONTRIBUTING.md` for guidelines on environment setup, coding standards, and workflow expectations. A `CODE_OF_CONDUCT.md` outlines community behavior expectations.

## Licensing
This repository is released under the MIT License. See `LICENSE` for details.

## Migration Notes
Changes from the original single README have been captured in `MIGRATION_NOTES.md`, preserving prior portfolio content for historical reference.
