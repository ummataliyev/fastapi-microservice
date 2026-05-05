PROJECT_NAME = template-service
DOCKER_COMPOSE = docker compose -p $(PROJECT_NAME) -f infra/docker-compose.yaml
API_SERVICE = app
DC_EXEC = $(DOCKER_COMPOSE) exec -T $(API_SERVICE)
DC_EXEC_IT = $(DOCKER_COMPOSE) exec $(API_SERVICE)

.DEFAULT_GOAL := help

install:
	uv sync

up:
	$(DOCKER_COMPOSE) up --build -d

down:
	$(DOCKER_COMPOSE) down --remove-orphans

restart:
	$(DOCKER_COMPOSE) restart $(API_SERVICE)

logs:
	$(DOCKER_COMPOSE) logs -f

logs-api:
	$(DOCKER_COMPOSE) logs -f $(API_SERVICE)

shell:
	$(DC_EXEC_IT) bash

clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans

build:
	$(DOCKER_COMPOSE) build

upgrade:
	$(DC_EXEC) alembic upgrade head

migrate:
	$(DC_EXEC) alembic upgrade head

revision:
	@read -p "Migration comment: " msg; \
	$(DC_EXEC) alembic revision --autogenerate -m "$$msg"

lint:
	uv run ruff check src

format:
	uv run ruff check src --fix
	uv run ruff format src

check:
	uv run ruff check src

dev:
	set -a && . infra/.env && set +a && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run:
	set -a && . infra/.env && set +a && uv run gunicorn src.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies with uv"
	@echo "  make up          - Build and start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart API container"
	@echo "  make logs        - Show all logs"
	@echo "  make logs-api    - Show API logs"
	@echo "  make shell       - Bash into API container"
	@echo "  make build       - Build Docker images"
	@echo "  make clean       - Remove all containers & volumes"
	@echo "  make upgrade     - Apply all migrations"
	@echo "  make migrate     - Run migrations"
	@echo "  make revision    - Create new migration"
	@echo "  make lint        - Run Ruff lint"
	@echo "  make format      - Auto-format code"
	@echo "  make check       - Run lint checks"
	@echo "  make dev         - Run dev server with hot reload"
	@echo "  make run         - Run production server locally"
