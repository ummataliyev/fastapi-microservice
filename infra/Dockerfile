# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/.venv \
    UV_PROJECT_ENVIRONMENT=/.venv \
    PATH="/.venv/bin:$PATH"

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

FROM base AS deps-dev
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    python -m venv "$VENV_PATH" \
    && uv sync --frozen --python "$VENV_PATH/bin/python"

FROM base AS deps-prod
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    python -m venv "$VENV_PATH" \
    && uv sync --frozen --no-dev --python "$VENV_PATH/bin/python"

FROM base AS dev
COPY --from=deps-dev /.venv /.venv
COPY . .
RUN chmod +x ./infra/commands/*.sh
ENTRYPOINT ["/app/infra/commands/entrypoint.sh"]
CMD ["/app/infra/commands/api.sh"]

FROM base AS prod
COPY --from=deps-prod /.venv /.venv
COPY alembic.ini ./alembic.ini
COPY src ./src
COPY infra/commands ./infra/commands
RUN chmod +x ./infra/commands/*.sh \
    && useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p logs && chown -R appuser:appuser logs
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/template/health || exit 1
ENTRYPOINT ["/app/infra/commands/entrypoint.sh"]
CMD ["/app/infra/commands/api.sh"]
