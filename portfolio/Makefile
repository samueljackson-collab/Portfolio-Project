PYTHON := python3
FRONTEND_DIR := projects/frontend
BACKEND_DIR := projects/backend

.PHONY: bootstrap backend-install frontend-install lint lint-backend lint-frontend test test-backend test-frontend format start-backend start-frontend compose-up compose-down security-check pre-commit docs

bootstrap: backend-install frontend-install

backend-install:
$(PYTHON) -m pip install --upgrade pip
$(PYTHON) -m pip install -r requirements.txt

frontend-install:
npm install --prefix $(FRONTEND_DIR)

lint: lint-backend lint-frontend

lint-backend:
ruff check $(BACKEND_DIR)/app $(BACKEND_DIR)/tests

lint-frontend:
npm run lint --prefix $(FRONTEND_DIR)

test: test-backend test-frontend

test-backend:
pytest --cov=$(BACKEND_DIR)/app --cov-report=term-missing --cov-fail-under=80 $(BACKEND_DIR)/tests

test-frontend:
npm test --prefix $(FRONTEND_DIR) -- --run

format:
ruff format $(BACKEND_DIR)/app $(BACKEND_DIR)/tests
npm run format --prefix $(FRONTEND_DIR)

start-backend:
uvicorn projects.backend.app.main:app --reload --host 0.0.0.0 --port 8000

start-frontend:
npm run dev --prefix $(FRONTEND_DIR)

compose-up:
docker compose up --build

compose-down:
docker compose down

security-check:
bandit -r $(BACKEND_DIR)/app
npm run audit

pre-commit:
pre-commit run --all-files

docs:
@echo "Docs available under docs/"
