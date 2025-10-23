FROM python:3.11.2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT="/.venv/"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY . .

RUN chmod +x ./infra/commands/*.sh

ENTRYPOINT ["/app/infra/commands/entrypoint.sh"]

CMD ["uv", "run", "gunicorn", "src.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]
