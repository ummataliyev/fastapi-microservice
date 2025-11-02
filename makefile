PROJECT_NAME = fastapi-microservice
DOCKER_COMPOSE = docker compose -p $(PROJECT_NAME) -f infra/docker-compose.local.yml
API_CONTAINER = micro-service-api
DB_CONTAINER = micro-service-db
DC_EXEC = docker exec -it $(API_CONTAINER)

.DEFAULT_GOAL := help

up:
	$(DOCKER_COMPOSE) up --build -d

down:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) restart $(API_CONTAINER)

logs:
	$(DOCKER_COMPOSE) logs -f

shell:
	$(DC_EXEC) bash

psql:
	docker exec -it $(DB_CONTAINER) psql -U $$POSTGRES_USER $$POSTGRES_DB

clean:
	$(DOCKER_COMPOSE) down -v

build:
	$(DOCKER_COMPOSE) build

upgrade:
	$(DC_EXEC) uv run alembic upgrade head

revision:
	@read -p "Migration comment: " msg; \
	$(DC_EXEC) uv run alembic revision --autogenerate -m "$$msg"

test:
	$(DC_EXEC) uv run pytest -vvv --capture=no --rootdir=src/tests src/tests $(TEST_ARGS)

lint:
	uv run ruff check src

format:
	uv run ruff check src --fix
	uv run ruff format src

help:
	@echo "Available commands:"
	@echo "  make up          - Build and start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart API container"
	@echo "  make logs        - Show logs"
	@echo "  make shell       - Bash into API container"
	@echo "  make psql        - Connect to Postgres (uses env DB and USER)"
	@echo "  make build       - Build Docker images"
	@echo "  make clean       - Remove all containers & volumes"
	@echo "  make upgrade     - Apply all migrations"
	@echo "  make revision    - Create new migration (asks for comment)"
	@echo "  make test        - Run tests (pass TEST_ARGS for extra pytest args)"
	@echo "  make lint        - Run Ruff lint"
	@echo "  make format      - Auto-format code"
