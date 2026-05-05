#!/bin/sh
set -e

WORKERS=${GUNICORN_WORKERS:-4}
BIND=${GUNICORN_BIND:-0.0.0.0:8000}
TIMEOUT=${GUNICORN_TIMEOUT:-120}

exec uv run gunicorn src.main:app \
  --workers "${WORKERS}" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind "${BIND}" \
  --timeout "${TIMEOUT}" \
  --access-logfile - \
  --error-logfile -
