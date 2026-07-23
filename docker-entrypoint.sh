#!/bin/sh
set -eu

if [ -n "${DB_HOST:-}" ]; then
  export DATABASE_URL="postgresql+psycopg://${DB_USER:-web}:${DB_PASSWORD:-web}@${DB_HOST}:${DB_PORT:-5432}/${DB_NAME:-web}"
fi

alembic upgrade head
python -m app.seed

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
