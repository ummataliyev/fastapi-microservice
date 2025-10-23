#!/bin/bash
# Выход из скрипта при любой ошибке
set -e

# Ожидание готовности PostgreSQL
echo "Waiting for postgres..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -q; do
  sleep 1
done
echo "PostgreSQL is up - executing command"

# Применение миграций Alembic
echo "Applying database migrations..."
uv run alembic upgrade head
echo "Migrations applied successfully."

# Запуск основного процесса (команды, переданной в CMD Dockerfile)
exec "$@"
