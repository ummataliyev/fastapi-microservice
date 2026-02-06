#!/bin/bash
set -e

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

wait_for_mongo() {
  echo "Waiting for MongoDB..."
  until uv run python - <<'PY'
from pymongo import MongoClient
import os

host = os.environ.get("MONGO_HOST", "mongo")
port = int(os.environ.get("MONGO_PORT", "27017"))
user = os.environ.get("MONGO_USER") or None
password = os.environ.get("MONGO_PASSWORD") or None

kwargs = {"host": host, "port": port, "serverSelectionTimeoutMS": 1000}
if user and password:
    kwargs.update({"username": user, "password": password})

client = MongoClient(**kwargs)
client.admin.command("ping")
client.close()
PY
  do
    sleep 1
  done
  echo "MongoDB is up."
}

case "$DB_PROVIDER" in
  postgres) wait_for_postgres ;;
  mysql) wait_for_mysql ;;
  mongo) wait_for_mongo ;;
  *)
    echo "Unsupported DB_PROVIDER: $DB_PROVIDER"
    exit 1
    ;;
esac

RUN_MIGRATIONS_ON_START="${RUN_MIGRATIONS_ON_START:-true}"
RUN_MIGRATIONS_ON_START="$(echo "$RUN_MIGRATIONS_ON_START" | tr '[:upper:]' '[:lower:]')"
if [[ "$RUN_MIGRATIONS_ON_START" == "true" || "$RUN_MIGRATIONS_ON_START" == "1" || "$RUN_MIGRATIONS_ON_START" == "yes" ]]; then
  if [[ "$DB_PROVIDER" == "mongo" ]]; then
    echo "Skipping Alembic migrations for MongoDB provider."
  else
    echo "Applying database migrations..."
    uv run alembic upgrade head
    echo "Migrations applied successfully."
  fi
else
  echo "Skipping migrations (RUN_MIGRATIONS_ON_START=$RUN_MIGRATIONS_ON_START)."
fi

exec "$@"
