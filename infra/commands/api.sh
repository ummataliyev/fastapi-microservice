#!/bin/bash
set -euo pipefail

# Runtime-tunable Gunicorn settings with production-safe defaults.
GUNICORN_BIND="${GUNICORN_BIND:-0.0.0.0:8000}"
GUNICORN_WORKER_CLASS="${GUNICORN_WORKER_CLASS:-uvicorn.workers.UvicornWorker}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-60}"
GUNICORN_GRACEFUL_TIMEOUT="${GUNICORN_GRACEFUL_TIMEOUT:-30}"
GUNICORN_KEEPALIVE="${GUNICORN_KEEPALIVE:-5}"
GUNICORN_MAX_REQUESTS="${GUNICORN_MAX_REQUESTS:-1000}"
GUNICORN_MAX_REQUESTS_JITTER="${GUNICORN_MAX_REQUESTS_JITTER:-100}"
GUNICORN_LOG_LEVEL="${GUNICORN_LOG_LEVEL:-info}"
GUNICORN_ACCESSLOG="${GUNICORN_ACCESSLOG:--}"
GUNICORN_ERRORLOG="${GUNICORN_ERRORLOG:--}"
GUNICORN_WORKER_TMP_DIR="${GUNICORN_WORKER_TMP_DIR:-/dev/shm}"

if [[ -z "${WEB_CONCURRENCY:-}" ]]; then
  if command -v nproc >/dev/null 2>&1; then
    cores="$(nproc)"
    WEB_CONCURRENCY="$((cores * 2 + 1))"
  else
    WEB_CONCURRENCY="2"
  fi
fi

exec /bin/uv run gunicorn src.main:app \
  --worker-class "${GUNICORN_WORKER_CLASS}" \
  --bind "${GUNICORN_BIND}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout "${GUNICORN_TIMEOUT}" \
  --graceful-timeout "${GUNICORN_GRACEFUL_TIMEOUT}" \
  --keep-alive "${GUNICORN_KEEPALIVE}" \
  --max-requests "${GUNICORN_MAX_REQUESTS}" \
  --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER}" \
  --log-level "${GUNICORN_LOG_LEVEL}" \
  --access-logfile "${GUNICORN_ACCESSLOG}" \
  --error-logfile "${GUNICORN_ERRORLOG}" \
  --worker-tmp-dir "${GUNICORN_WORKER_TMP_DIR}"
