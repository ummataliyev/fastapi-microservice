# fastapi-microservice

A production-ready FastAPI template with postgres, JWT auth, structured exceptions, and a worked auth/users example.

## Stack

- FastAPI 0.115 / Starlette
- SQLAlchemy 2.0 (async) + asyncpg + Alembic
- Pydantic 2 / pydantic-settings
- PyJWT + passlib[bcrypt]
- fastapi-pagination, prometheus-fastapi-instrumentator, sentry-sdk
- APScheduler (lifespan-driven)
- uv + ruff + pre-commit

## Layout

```
src/
├── api/                     # routers, dependencies, custom middlewares, exception handlers
├── core/                    # settings, JWT config, postgres config, logging, timezone
├── db/                      # async engine, session factory, mixins, declarative base
├── enums/
├── exceptions/
│   ├── repositories/
│   └── services/            # raised by services; auto-translated to JSON 4xx/5xx
├── integrations/
├── jobs/lifespan.py         # APScheduler entry; register cron jobs here
├── managers/db/             # TransactionManager / ReadonlyManager — wire repos here
├── mappers/                 # ORM ↔ Pydantic translation
├── migrations/              # Alembic
├── models/                  # SQLAlchemy ORM models
├── repositories/            # CRUD on models, returns mapped entities
├── schemas/                 # Pydantic request/response schemas
├── security/                # JWT + bcrypt (interfaces + implementations)
├── services/                # business logic (BaseService[TM])
└── tests/
```

## Quickstart

```bash
git clone <fork>
cd fastapi-microservice

cp infra/.env.example infra/.env
# edit infra/.env with your local DB_* and JWT_SECRET_KEY

# bring up postgres
docker compose -f infra/docker-compose.yaml up -d postgres

uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

Open `http://localhost:8000/template/docs` (basic auth: `admin` / `admin` — see `Settings.docs_password`).

## Endpoints

- `POST /template/api/v1/auth/register` — create a user, returns access + refresh tokens
- `POST /template/api/v1/auth/login` — exchange credentials for tokens
- `POST /template/api/v1/auth/refresh` — exchange a refresh token for a new pair
- `GET  /template/api/v1/auth/me` — JWT payload of the current user
- `GET  /template/api/v1/users` — paginated list (auth required)
- `GET  /template/api/v1/users/{id}`
- `POST /template/api/v1/users`
- `PATCH /template/api/v1/users/{id}`
- `DELETE /template/api/v1/users/{id}`
- `GET  /template/health`
- `GET  /template/ready`
- `GET  /template/metrics` (Prometheus)

## Production checklist

Before exposing this template publicly, change the defaults:

- `JWT_SECRET_KEY` — generate with `openssl rand -hex 32`. The default `change-me-in-prod` is unsafe and PyJWT will warn.
- `CORS_ALLOW_ORIGINS` — set to the explicit list of front-end origins (e.g. `["https://app.example.com"]`). The default `["*"]` is for local dev only.
- `DOCS_USERNAME` / `DOCS_PASSWORD` — change or disable the basic-auth-protected `/template/docs` endpoint.
- `DB_PASSWORD` — pick a strong password and inject via secrets manager, not `infra/.env`.
- `SENTRY_DSN` — optional but recommended; sentry integration is wired in `src/main.py`.

## Customizing for a new service

1. Find/replace `/template/` with `/<your-service>/` across `src/main.py` and `src/api/v1/__init__.py`.
2. Rename in `pyproject.toml`: `[project] name`, `[tool.hatch.build.targets.wheel] packages` (already `["src"]`).
3. Add domain models, schemas, mappers, repositories, services, routers — follow the `users` example.
4. Wire new repositories in `src/managers/db/transaction.py` and `readonly.py`.
5. Register your routers in `src/api/v1/__init__.py`.

## Running tests

```bash
uv run pytest src/tests/ -v
```

## License

MIT
