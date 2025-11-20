SHELL := /bin/bash
INFRA_DIR := $$(CURDIR)/infrastructure
ENV_FILE := $$(INFRA_DIR)/.env
COMPOSE := docker compose --env-file $$(ENV_FILE) -f $$(INFRA_DIR)/docker-compose.yml

.PHONY: help bootstrap start stop restart status validate logs

help:
	@echo "Available targets:"
	@echo "  make bootstrap   # Pull images and launch the stack"
	@echo "  make start       # Start services without pulling"
	@echo "  make stop        # Stop and remove the stack"
	@echo "  make restart     # Restart the stack"
	@echo "  make status      # Show docker compose ps"
	@echo "  make validate    # Run health checks"
	@echo "  make logs        # Tail all logs (Ctrl+C to exit)"

bootstrap:
	scripts/bootstrap_stack.sh

start:
	@if [ ! -f $$(ENV_FILE) ]; then \
		echo "Missing $$(ENV_FILE). Copy infrastructure/.env.example first." >&2; \
		exit 1; \
	fi
	$$(COMPOSE) up -d

stop:
	scripts/shutdown_stack.sh

restart: stop start

status:
	@if [ ! -f $$(ENV_FILE) ]; then \
		echo "Missing $$(ENV_FILE). Copy infrastructure/.env.example first." >&2; \
		exit 1; \
	fi
	$$(COMPOSE) ps

validate:
	scripts/validate_stack.sh

logs:
	@if [ ! -f $$(ENV_FILE) ]; then \
		echo "Missing $$(ENV_FILE). Copy infrastructure/.env.example first." >&2; \
		exit 1; \
	fi
	$$(COMPOSE) logs -f
