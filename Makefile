PYTHON ?= python3
PIP ?= pip3
NPM ?= npm
DOCKER_COMPOSE ?= docker compose

.PHONY: help install dev stop backend frontend monitoring tests lint fmt clean generate-manifest package

help:
@echo "Available targets:"
@echo "  install            Install Python and Node dependencies"
@echo "  dev                Start local development environment"
@echo "  stop               Stop local development environment"
@echo "  backend            Run backend service"
@echo "  frontend           Run frontend service"
@echo "  monitoring         Run monitoring exporter"
@echo "  tests              Run backend unit tests"
@echo "  lint               Run linting across services"
@echo "  fmt                Format frontend code"
@echo "  clean              Remove build artifacts"
@echo "  generate-manifest  Generate repository manifest"
@echo "  package            Create release archive"

install:
$(PIP) install -r requirements.txt
$(PIP) install -r backend/requirements.txt
cd frontend && $(NPM) install
cd monitoring && $(PIP) install -r requirements.txt

backend:
cd backend && uvicorn app.main:app --reload

frontend:
cd frontend && $(NPM) run dev

monitoring:
cd monitoring && uvicorn app.main:app --reload --port 9090

tests:
cd backend && pytest

lint:
pre-commit run --all-files

fmt:
cd frontend && $(NPM) run format

clean:
rm -rf **/__pycache__
rm -rf frontend/node_modules frontend/dist
rm -rf .pytest_cache backend/.pytest_cache
rm -rf infra/.terraform

generate-manifest:
$(PYTHON) tools/gen_manifest.py --output data/master_repo_manifest_v1.4.json

package:
./scripts/package_zip.sh

dev:
$(DOCKER_COMPOSE) up --build

stop:
$(DOCKER_COMPOSE) down
