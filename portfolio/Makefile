SHELL := /bin/bash

.PHONY: dev up down test fmt build

dev: up
up:
docker compose -f compose/docker-compose.yml --env-file compose/.env.example up -d --build
down:
docker compose -f compose/docker-compose.yml --env-file compose/.env.example down -v
test:
cd backend && pytest -q --maxfail=1 --disable-warnings --cov=app
fmt:
ruff check --fix backend || true; black backend || true; isort backend || true
prettier -w frontend || true; eslint -c frontend/.eslintrc.cjs "frontend/src/**/*.{ts,tsx}" || true
build:
cd frontend && npm ci && npm run build
docker build -t portfolio-frontend:local ./frontend
docker build -t portfolio-backend:local ./backend
