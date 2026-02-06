#!/bin/bash
set -euo pipefail

DB_PROVIDER="${DB_PROVIDER:-postgres}"
DB_PROVIDER="$(echo "$DB_PROVIDER" | tr '[:upper:]' '[:lower:]')"

wait_for_postgres() {
  echo "Waiting for PostgreSQL..."
  while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -q; do
    sleep 1
  done
  echo "PostgreSQL is up."
}

wait_for_mysql() {
  echo "Waiting for MySQL..."
  while ! mysqladmin ping -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" "-p$MYSQL_PASSWORD" --silent; do
    sleep 1
  done
  echo "MySQL is up."
}

case "$DB_PROVIDER" in
  postgres)
    wait_for_postgres
    echo "Running Alembic migrations for PostgreSQL..."
    uv run alembic upgrade head
    ;;
  mysql)
    wait_for_mysql
    echo "Running Alembic migrations for MySQL..."
    uv run alembic upgrade head
    ;;
  mongo)
    echo "Skipping Alembic for MongoDB provider."
    ;;
  *)
    echo "Unsupported DB_PROVIDER: $DB_PROVIDER"
    exit 1
    ;;
esac
