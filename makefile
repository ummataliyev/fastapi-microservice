PROJECT_NAME = fastapi-microservice
DOCKER_COMPOSE = docker compose -p $(PROJECT_NAME) -f infra/docker-compose.local.yml
API_SERVICE = api
DB_SERVICE = db
DC_EXEC = $(DOCKER_COMPOSE) exec -T $(API_SERVICE)
DC_EXEC_IT = $(DOCKER_COMPOSE) exec $(API_SERVICE)
BUILDX_BUILDER ?= fastapi-microservice-builder
IMAGE ?= fastapi-microservice-api:latest
PLATFORM ?= linux/amd64
PLATFORMS ?= linux/amd64,linux/arm64
DB_PROVIDER ?= $(shell awk -F= '/^DB_PROVIDER=/{print $$2}' infra/.env | tr -d '[:space:]')
COMPOSE_PROFILES ?= $(DB_PROVIDER)
ALL_PROFILES = postgres,mysql,mongo

.DEFAULT_GOAL := help

up:
	DB_PROVIDER=$(DB_PROVIDER) COMPOSE_PROFILES=$(COMPOSE_PROFILES) $(DOCKER_COMPOSE) up --build -d

up-postgres:
	DB_PROVIDER=postgres COMPOSE_PROFILES=postgres $(DOCKER_COMPOSE) up --build -d

up-mysql:
	DB_PROVIDER=mysql COMPOSE_PROFILES=mysql $(DOCKER_COMPOSE) up --build -d

up-mongo:
	DB_PROVIDER=mongo COMPOSE_PROFILES=mongo $(DOCKER_COMPOSE) up --build -d

down:
	COMPOSE_PROFILES=$(ALL_PROFILES) $(DOCKER_COMPOSE) down --remove-orphans

restart:
	$(DOCKER_COMPOSE) restart $(API_SERVICE)

logs:
	$(DOCKER_COMPOSE) logs -f

shell:
	$(DC_EXEC_IT) bash

psql:
	$(DOCKER_COMPOSE) exec $(DB_SERVICE) psql -U $$POSTGRES_USER $$POSTGRES_DB

clean:
	COMPOSE_PROFILES=$(ALL_PROFILES) $(DOCKER_COMPOSE) down -v --remove-orphans

build:
	DB_PROVIDER=$(DB_PROVIDER) COMPOSE_PROFILES=$(COMPOSE_PROFILES) $(DOCKER_COMPOSE) build

buildx-create:
	docker buildx create --name $(BUILDX_BUILDER) --use || docker buildx use $(BUILDX_BUILDER)
	docker buildx inspect --bootstrap

buildx-build:
	docker buildx build --builder $(BUILDX_BUILDER) --platform $(PLATFORM) -f infra/Dockerfile --target prod -t $(IMAGE) --load .

buildx-push:
	docker buildx build --builder $(BUILDX_BUILDER) --platform $(PLATFORMS) -f infra/Dockerfile --target prod -t $(IMAGE) --push .

upgrade:
	$(DC_EXEC) bash ./infra/commands/migrate.sh

migrate:
	$(DC_EXEC) bash ./infra/commands/migrate.sh

revision:
	@read -p "Migration comment: " msg; \
	$(DC_EXEC) uv run alembic revision --autogenerate -m "$$msg"

test:
	$(DC_EXEC) uv run pytest -vvv --capture=no --rootdir=src/tests src/tests $(TEST_ARGS)

test-local:
	uv run pytest -q src/tests $(TEST_ARGS)

test-unit:
	uv run pytest -q src/tests/unit

lint:
	uv run ruff check src

format:
	uv run ruff check src --fix
	uv run ruff format src

check:
	uv run ruff check src
	uv run pytest -q src/tests/unit

help:
	@echo "Available commands:"
	@echo "  make up          - Build and start all services"
	@echo "                     Uses DB_PROVIDER from infra/.env to select profile automatically"
	@echo "  make up-postgres - Start with PostgreSQL provider (profile postgres)"
	@echo "  make up-mysql    - Start with MySQL provider (profile mysql)"
	@echo "  make up-mongo    - Start with MongoDB provider (profile mongo)"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart API container"
	@echo "  make logs        - Show logs"
	@echo "  make shell       - Bash into API container"
	@echo "  make psql        - Connect to Postgres (uses env DB and USER)"
	@echo "  make build       - Build Docker images"
	@echo "  make buildx-create - Create/select buildx builder"
	@echo "  make buildx-build  - Build single-platform prod image locally (override IMAGE/PLATFORM)"
	@echo "  make buildx-push   - Build and push multi-arch prod image (override IMAGE/PLATFORMS)"
	@echo "  make clean       - Remove all containers & volumes"
	@echo "  make upgrade     - Apply all migrations from running API container"
	@echo "  make migrate     - Run migrations from running API container"
	@echo "  make revision    - Create new migration (asks for comment)"
	@echo "  make test        - Run tests (pass TEST_ARGS for extra pytest args)"
	@echo "  make test-local  - Run all tests locally with current environment"
	@echo "  make test-unit   - Run unit tests only"
	@echo "  make lint        - Run Ruff lint"
	@echo "  make format      - Auto-format code"
	@echo "  make check       - Run lint + unit tests"
