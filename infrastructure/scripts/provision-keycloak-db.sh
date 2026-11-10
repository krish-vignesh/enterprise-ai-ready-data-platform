
#!/bin/sh

set -eu

: "${POSTGRES_HOST:=postgres}"
: "${POSTGRES_PORT:=5432}"

: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"

: "${KEYCLOAK_DB_NAME:?KEYCLOAK_DB_NAME is required}"
: "${KEYCLOAK_DB_USER:?KEYCLOAK_DB_USER is required}"
: "${KEYCLOAK_DB_PASSWORD:?KEYCLOAK_DB_PASSWORD is required}"

export PGPASSWORD="$POSTGRES_PASSWORD"

psql \
    --host="$POSTGRES_HOST" \
    --port="$POSTGRES_PORT" \
    --username="$POSTGRES_USER" \
    --dbname="$POSTGRES_DB" \
    --set=ON_ERROR_STOP=1 <<'SQL'

\getenv keycloak_db_name KEYCLOAK_DB_NAME
\getenv keycloak_db_user KEYCLOAK_DB_USER
\getenv keycloak_db_password KEYCLOAK_DB_PASSWORD

-- Create the dedicated Keycloak database role if absent.
SELECT format(
    'CREATE ROLE %I WITH LOGIN PASSWORD %L',
    :'keycloak_db_user',
    :'keycloak_db_password'
)
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_roles
    WHERE rolname = :'keycloak_db_user'
)
\gexec

-- Synchronize the role password with the configured secret.
SELECT format(
    'ALTER ROLE %I WITH LOGIN PASSWORD %L',
    :'keycloak_db_user',
    :'keycloak_db_password'
)
\gexec

-- Create the Keycloak database if absent.
SELECT format(
    'CREATE DATABASE %I OWNER %I',
    :'keycloak_db_name',
    :'keycloak_db_user'
)
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_database
    WHERE datname = :'keycloak_db_name'
)
\gexec

-- Ensure the intended owner.
SELECT format(
    'ALTER DATABASE %I OWNER TO %I',
    :'keycloak_db_name',
    :'keycloak_db_user'
)
\gexec

-- Grant database privileges.
SELECT format(
    'GRANT ALL PRIVILEGES ON DATABASE %I TO %I',
    :'keycloak_db_name',
    :'keycloak_db_user'
)
\gexec

SQL

unset PGPASSWORD

echo "Keycloak database provisioning completed successfully."
