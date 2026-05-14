.PHONY: help bootstrap up down logs ps rebuild \
        backend-shell db-shell \
        lint format \
        test test-backend test-frontend \
        clean pre-commit

## ─── General ─────────────────────────────────────────────────────────────────

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

bootstrap: ## First-time setup: copy .env, pull images, build dev images, install pre-commit hooks
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example — review and update values."; fi
	docker compose pull postgres
	docker compose build
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "Bootstrap complete. Run 'make up' to start the stack."

## ─── Stack ───────────────────────────────────────────────────────────────────

up: ## Start all services in the background
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Follow logs for all services (Ctrl-C to stop)
	docker compose logs -f

ps: ## Show running service status
	docker compose ps

rebuild: ## Rebuild images from scratch and recreate containers
	docker compose build --no-cache
	docker compose up -d --force-recreate

## ─── Shells ──────────────────────────────────────────────────────────────────

backend-shell: ## Open a bash shell in the backend container
	docker compose exec backend bash

db-shell: ## Open a psql shell in the postgres container
	docker compose exec postgres psql -U $${POSTGRES_USER:-foundry} -d $${POSTGRES_DB:-foundry}

## ─── Quality ─────────────────────────────────────────────────────────────────

lint: ## Run all linters (ruff, mypy, eslint, prettier-check)
	docker compose run --rm backend ruff check .
	docker compose run --rm backend mypy app/
	docker compose run --rm frontend npm run lint
	docker compose run --rm frontend npm run format:check

format: ## Auto-format all code (ruff, prettier)
	docker compose run --rm backend ruff format .
	docker compose run --rm backend ruff check --fix .
	docker compose run --rm frontend npm run format

pre-commit: ## Run all pre-commit hooks against every file
	pre-commit run --all-files

## ─── Tests ───────────────────────────────────────────────────────────────────

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests with pytest
	docker compose run --rm backend pytest tests/ -v

test-frontend: ## Run frontend tests with Vitest
	docker compose run --rm frontend npm run test

## ─── Cleanup ─────────────────────────────────────────────────────────────────

clean: ## Remove containers, volumes, and local build artifacts
	docker compose down -v --remove-orphans
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/dist frontend/.vite 2>/dev/null || true
