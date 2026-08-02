.PHONY: help dev dev-bg stop build test lint format migrate seed keys clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Development ──────────────────────────────────────────────────────────────

dev: ## Start all services (foreground)
	docker compose up --build

dev-bg: ## Start all services (background)
	docker compose up -d --build

stop: ## Stop all services
	docker compose down

logs: ## Follow logs for all services
	docker compose logs -f

logs-api: ## Follow API logs
	docker compose logs -f api

logs-worker: ## Follow worker logs
	docker compose logs -f worker

# ─── Keys ─────────────────────────────────────────────────────────────────────

keys: ## Generate RS256 JWT key pair
	@mkdir -p infrastructure/keys
	@openssl genrsa -out infrastructure/keys/jwt_private.pem 4096
	@openssl rsa -in infrastructure/keys/jwt_private.pem -pubout -out infrastructure/keys/jwt_public.pem
	@echo "✅ JWT RS256 key pair generated at infrastructure/keys/"

# ─── Database ─────────────────────────────────────────────────────────────────

migrate: ## Run Alembic migrations
	docker compose exec api alembic upgrade head

migrate-create: ## Create a new migration (name=<name>)
	docker compose exec api alembic revision --autogenerate -m "$(name)"

seed: ## Seed the database with initial data
	docker compose exec api python -m scripts.seed.main

db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U aigos -d aigos

redis-cli: ## Open Redis CLI
	docker compose exec redis redis-cli

# ─── Testing ──────────────────────────────────────────────────────────────────

test: ## Run all tests
	docker compose exec api pytest -v

test-unit: ## Run unit tests only
	docker compose exec api pytest domains/*/tests/unit/ -v

test-integration: ## Run integration tests only
	docker compose exec api pytest domains/*/tests/integration/ -v

test-cov: ## Run tests with coverage report
	docker compose exec api pytest --cov --cov-report=html

# ─── Code Quality ─────────────────────────────────────────────────────────────

lint: ## Lint Python code
	docker compose exec api ruff check .
	docker compose exec api mypy .

format: ## Format Python code
	docker compose exec api ruff format .

lint-web: ## Lint Next.js code
	docker compose exec web pnpm lint

# ─── Build ────────────────────────────────────────────────────────────────────

build: ## Build all Docker images
	docker compose build

build-api: ## Build API image only
	docker build -f infrastructure/docker/Dockerfile.api -t ai-gos/api:latest .

build-web: ## Build web image only
	docker build -f infrastructure/docker/Dockerfile.web -t ai-gos/web:latest .

# ─── Observability ────────────────────────────────────────────────────────────

grafana: ## Open Grafana in browser
	open http://localhost:3001

prometheus: ## Open Prometheus in browser
	open http://localhost:9090

api-docs: ## Open API documentation
	open http://localhost:8000/docs

# ─── Secrets Scan ─────────────────────────────────────────────────────────────

secrets-scan: ## Scan for hardcoded secrets (requires gitleaks)
	gitleaks detect --source . --verbose

# ─── Clean ────────────────────────────────────────────────────────────────────

clean: ## Remove all containers, volumes, build artifacts
	docker compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".coverage" -delete
