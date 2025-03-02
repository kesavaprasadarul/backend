#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -U "$POSTGRES_USER" -h localhost -p 5432; do
  >&2 echo "PostgreSQL is unavailable - waiting..."
  sleep 5
done

>&2 echo "PostgreSQL is up - testing connection with psql..."

# TEST CONNECTION - Add this block
if ! psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -h localhost -p 5432 -c 'SELECT 1;'; then
  >&2 echo "ERROR: psql connection test failed!"
  exit 1  # Exit script if connection test fails
fi

>&2 echo "psql connection test successful - restoring database..."

# Restore the database using pg_restore
pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" /docker-entrypoint-initdb.d/backup_20240602

>&2 echo "Database restore complete."