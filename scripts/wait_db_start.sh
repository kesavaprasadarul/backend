set -e; \
>&2 echo "Starting PostgreSQL service..."; \
set -e && \
export PGPASSWORD=$POSTGRES_PASSWORD; \
>&2 echo "Waiting for PostgreSQL to be ready..."; \
until pg_isready -U "$POSTGRES_USER" -h db -p 5432; do \
    >&2 echo "localhost:5432 - no response"; \
    >&2 echo "PostgreSQL is unavailable - waiting..."; \
    sleep 5; \
done; \
\
>&2 echo "PostgreSQL is up - testing connection with psql..."; \
if ! psql -d "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_SERVER/$POSTGRES_DB" -c 'SELECT 1;'; then \
    >&2 echo "ERROR: psql connection test failed!"; \
    service postgresql stop; \
    exit 1; \
fi; \
>&2 echo "psql connection test successful";