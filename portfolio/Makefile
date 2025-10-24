SHELL := /bin/bash
COMPOSE_FILE := compose/docker-compose.yml
COMPOSE_ENV := $(shell if [ -f compose/.env ]; then echo compose/.env; else echo compose/.env.example; fi)

.PHONY: dev up down test fmt build lint backend-test frontend-test infra-fmt tools-test bootstrap

dev: up

up:
	docker compose -f $(COMPOSE_FILE) --env-file $(COMPOSE_ENV) up -d --build

down:
	docker compose -f $(COMPOSE_FILE) --env-file $(COMPOSE_ENV) down -v

test: backend-test frontend-test tools-test

backend-test:
	cd backend && pytest

frontend-test:
	cd frontend && npm install --no-save && npm run typecheck

tools-test:
	python -m pytest -q tools/tests tools/dupefinder/tests

fmt: lint infra-fmt

lint:
	cd backend && ruff check . && black . && isort . && bandit -ll -r app
	cd frontend && npm install --no-save && npm run lint && npm run format

infra-fmt:
	cd infra && terraform fmt -recursive || true
	cd infra && tflint || true
	cd infra && tfsec || true

build:
	cd frontend && npm install --no-save && npm run build
	docker build -t portfolio-backend:local ./backend
	docker build -t portfolio-frontend:local ./frontend

bootstrap:
	python tools/bootstrap.py
