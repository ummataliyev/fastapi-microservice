# template-service

[Replace this with a one-paragraph description of what the service does.]

## Local development

```bash
cp infra/.env.example infra/.env       # edit secrets if needed
uv sync                                # install deps + create .venv
make dev                               # docker compose up -d (postgres + service on :8000)
```

The service serves on `http://localhost:8000/template/` with:
- `GET /template/health` — liveness check
- `GET /template/docs` — Swagger UI (basic auth: `${DOCS_USERNAME}` / `${DOCS_PASSWORD}`)
- `GET /template/metrics` — Prometheus scrape endpoint

## Make targets

| Target | What it does |
|--------|--------------|
| `make install` | `uv sync` |
| `make up` | `docker compose -f infra/docker-compose.yaml up -d` |
| `make down` | `docker compose -f infra/docker-compose.yaml down` |
| `make dev` | `make up` + tails logs |
| `make migrate` | `alembic upgrade head` |
| `make revision msg="..."` | `alembic revision --autogenerate -m "..."` |
| `make lint` | `ruff check src` |
| `make format` | `ruff format src` |

## Adding an entity

Use `examples/item.example.py` as a template. The example header lists the exact paths to copy each section into.

- `_active_filter` is mandatory for custom queries.
- TransactionManager wraps commit/rollback in `try/finally` (§6.4).
- Use `httpx`/`asyncio.sleep`, never `requests`/`time.sleep` (§6.5).
- Update endpoints accept both `PATCH` and `PUT` (§6.9).
- Pagination uses `sql_paginate` at the DB layer, never `paginate(list)` (§6.10).
