PROJECT_NAME=portfolio
COMPOSE_FILE=compose/docker-compose.yml
COMPOSE_ENV=compose/.env.example

.PHONY: dev test fmt build up down backend-test frontend-test lint

dev:
@docker compose -f $(COMPOSE_FILE) --env-file $(COMPOSE_ENV) up backend frontend db -d

backend-test:
@cd backend && pytest --maxfail=1 --disable-warnings -q

frontend-test:
@npm run test --workspace frontend -- --watch=false

test: backend-test frontend-test

fmt:
@ruff format backend/app
@npm run lint --workspace frontend
@npm run format --workspace frontend || true

lint:
@ruff check backend/app
@bandit -c pyproject.toml -r backend/app || true
@npm run lint --workspace frontend

build:
@docker compose -f $(COMPOSE_FILE) --env-file $(COMPOSE_ENV) build

up:
@docker compose -f $(COMPOSE_FILE) --env-file $(COMPOSE_ENV) up -d

down:
@docker compose -f $(COMPOSE_FILE) --env-file $(COMPOSE_ENV) down
