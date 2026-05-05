#!/bin/sh
set -e

echo "Waiting for Postgres at ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" >/dev/null 2>&1; do
  sleep 1
done
echo "Postgres ready."

if [ "${RUN_MIGRATIONS_ON_START:-true}" = "true" ]; then
  echo "Running alembic upgrade head..."
  uv run alembic upgrade head
fi

exec "$@"
