.PHONY: up down build logs shell-backend shell-frontend test lint dev-backend dev-frontend clean

# ── Docker (production-like) ─────────────────────────────────────────────────

up: ## Start all services (detached)
	docker-compose up --build -d

down: ## Stop all services
	docker-compose down

build: ## Rebuild images without starting
	docker-compose build

logs: ## Follow logs for both services
	docker-compose logs -f

shell-backend: ## Open a shell in the running backend container
	docker-compose exec backend sh

shell-frontend: ## Open a shell in the running frontend container
	docker-compose exec frontend sh

# ── Local development ────────────────────────────────────────────────────────

dev-backend: ## Run backend with hot-reload (requires .venv)
	cd backend && uvicorn main:app --reload --port 8000

dev-frontend: ## Run frontend dev server with HMR
	cd frontend && npm run dev

# ── Quality gates ────────────────────────────────────────────────────────────

test: ## Run backend tests
	cd backend && python -m pytest tests/ -v

lint: ## Type-check the frontend
	cd frontend && npm run type-check

# ── Setup ────────────────────────────────────────────────────────────────────

setup: ## First-time local setup: create venv, install deps, copy .env
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env && echo "Created backend/.env — edit it to configure"; fi
	cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt
	cd frontend && npm ci

clean: ## Remove build artifacts and caches
	cd frontend && rm -rf dist node_modules
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; rm -rf .venv data/*.db data/*.log .pytest_cache .mypy_cache

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
