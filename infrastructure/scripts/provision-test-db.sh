#!/usr/bin/env bash

set -Eeuo pipefail

log() {
    printf '%s\n' "$*"
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

cleanup() {
    if [ -n "${TMP_SQL_FILE:-}" ] && [ -f "$TMP_SQL_FILE" ]; then
        rm -f "$TMP_SQL_FILE"
    fi
    unset PGPASSWORD
}

escape_sql_literal() {
    local value=${1//\'/\'\'}
    printf "'%s'" "$value"
}

trap cleanup EXIT

: "${POSTGRES_HOST:?POSTGRES_HOST is required}"
: "${POSTGRES_PORT:?POSTGRES_PORT is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
: "${TEST_DB_NAME:?TEST_DB_NAME is required}"
: "${TEST_DB_USER:?TEST_DB_USER is required}"
: "${TEST_DB_PASSWORD:?TEST_DB_PASSWORD is required}"

PSQL_HOST="$POSTGRES_HOST"
PSQL_PORT="$POSTGRES_PORT"
if [ "${DOCKER_CONTAINER_PSQL:-0}" = "1" ]; then
    PSQL_HOST="localhost"
    PSQL_PORT="5432"
fi

if [ "$TEST_DB_NAME" != "enterprise_ai_platform_test_clean" ]; then
    fail "TEST_DB_NAME must be exactly enterprise_ai_platform_test_clean"
fi

if [ "$TEST_DB_USER" = "$POSTGRES_USER" ]; then
    fail "TEST_DB_USER must differ from the administrative PostgreSQL role"
fi

for role_name in "${APP_DB_USER:-}" "${KEYCLOAK_DB_USER:-}"; do
    if [ -n "$role_name" ] && [ "$role_name" = "$TEST_DB_USER" ]; then
        fail "TEST_DB_USER must be distinct from known application or Keycloak roles"
    fi
done

export PGPASSWORD="$POSTGRES_PASSWORD"
TMP_SQL_FILE=$(mktemp)
chmod 600 "$TMP_SQL_FILE"

cat > "$TMP_SQL_FILE" <<SQL
DO \$\$
DECLARE
    role_rec record;
    target_owner text;
    db_count integer;
BEGIN
    SELECT rolname, rolcanlogin, rolinherit, rolsuper, rolcreatedb, rolcreaterole, rolreplication, rolbypassrls
     INTO role_rec
     FROM pg_roles
     WHERE rolname = $(escape_sql_literal "$TEST_DB_USER");

    IF role_rec.rolname IS NOT NULL THEN
       IF role_rec.rolsuper OR role_rec.rolcreatedb OR role_rec.rolcreaterole OR role_rec.rolreplication OR role_rec.rolbypassrls THEN
           RAISE EXCEPTION 'Test role has unexpected administrative privileges';
       END IF;
       IF NOT role_rec.rolcanlogin THEN
           RAISE EXCEPTION 'Test role is missing LOGIN';
       END IF;
       IF role_rec.rolinherit THEN
           RAISE EXCEPTION 'Test role must have NOINHERIT';
       END IF;
       IF EXISTS (
           SELECT 1
             FROM pg_auth_members m
             JOIN pg_roles r ON r.oid = m.member
            WHERE r.rolname = $(escape_sql_literal "$TEST_DB_USER")
       ) THEN
           RAISE EXCEPTION 'Test role has direct role memberships';
       END IF;
    END IF;

    SELECT r.rolname INTO target_owner
     FROM pg_database d
     JOIN pg_roles r ON r.oid = d.datdba
     WHERE d.datname = $(escape_sql_literal "$TEST_DB_NAME");

    IF target_owner IS NOT NULL AND target_owner <> $(escape_sql_literal "$TEST_DB_USER") THEN
       RAISE EXCEPTION 'Target database already exists with unexpected owner';
    END IF;

    SELECT COUNT(*) INTO db_count
     FROM pg_database d
     JOIN pg_roles r ON r.oid = d.datdba
     WHERE r.rolname = $(escape_sql_literal "$TEST_DB_USER")
      AND d.datname <> $(escape_sql_literal "$TEST_DB_NAME");

    IF db_count > 0 THEN
       RAISE EXCEPTION 'Test role owns unrelated databases';
    END IF;
END \$\$;
SQL

psql \
    --host="$PSQL_HOST" \
    --port="$PSQL_PORT" \
    --username="$POSTGRES_USER" \
    --dbname="$POSTGRES_DB" \
    --set=ON_ERROR_STOP=1 \
    -f - < "$TMP_SQL_FILE"

TARGET_DB_EXISTS=$(psql \
    --host="$PSQL_HOST" \
    --port="$PSQL_PORT" \
    --username="$POSTGRES_USER" \
    --dbname="$POSTGRES_DB" \
    --tuples-only \
    --no-align \
    --quiet \
    -c "SELECT 1 FROM pg_database WHERE datname = $(escape_sql_literal "$TEST_DB_NAME");")

if [ "$TARGET_DB_EXISTS" = "1" ]; then
    cat > "$TMP_SQL_FILE" <<SQL
DO \$\$
DECLARE
    owner text;
    unexpected record;
BEGIN
    SELECT r.rolname INTO owner
     FROM pg_database d
     JOIN pg_roles r ON r.oid = d.datdba
     WHERE d.datname = $(escape_sql_literal "$TEST_DB_NAME");

    IF owner IS NULL OR owner <> $(escape_sql_literal "$TEST_DB_USER") THEN
       RAISE EXCEPTION 'Target database exists with unexpected owner';
    END IF;

    SELECT n.nspname, c.relname
     INTO unexpected
     FROM pg_class c
     JOIN pg_namespace n ON n.oid = c.relnamespace
     JOIN pg_roles r ON r.oid = c.relowner
     WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
      AND c.relkind IN ('r', 'p', 'S', 'v', 'm', 'f')
      AND r.rolname <> $(escape_sql_literal "$TEST_DB_USER")
     ORDER BY n.nspname, c.relname
     LIMIT 1;

    IF unexpected.relname IS NOT NULL THEN
       RAISE EXCEPTION 'Target database contains objects owned by another role';
    END IF;
END \$\$;
SQL

    psql \
       --host="$PSQL_HOST" \
       --port="$PSQL_PORT" \
       --username="$POSTGRES_USER" \
       --dbname="$TEST_DB_NAME" \
       --set=ON_ERROR_STOP=1 \
       -f - < "$TMP_SQL_FILE"
fi

cat > "$TMP_SQL_FILE" <<SQL
SELECT format(
    'CREATE ROLE %I WITH LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD %L',
    $(escape_sql_literal "$TEST_DB_USER"),
    $(escape_sql_literal "$TEST_DB_PASSWORD")
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_roles WHERE rolname = $(escape_sql_literal "$TEST_DB_USER")
)
\gexec
SQL

psql \
    --host="$PSQL_HOST" \
    --port="$PSQL_PORT" \
    --username="$POSTGRES_USER" \
    --dbname="$POSTGRES_DB" \
    --set=ON_ERROR_STOP=1 \
    -f - < "$TMP_SQL_FILE"

cat > "$TMP_SQL_FILE" <<SQL
SELECT format(
    'CREATE DATABASE %I OWNER %I',
    $(escape_sql_literal "$TEST_DB_NAME"),
    $(escape_sql_literal "$TEST_DB_USER")
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = $(escape_sql_literal "$TEST_DB_NAME")
)
\gexec
SQL

psql \
    --host="$PSQL_HOST" \
    --port="$PSQL_PORT" \
    --username="$POSTGRES_USER" \
    --dbname="$POSTGRES_DB" \
    --set=ON_ERROR_STOP=1 \
    -f - < "$TMP_SQL_FILE"

if [ "$TARGET_DB_EXISTS" = "1" ]; then
    cat > "$TMP_SQL_FILE" <<SQL
SELECT nspowner::regrole::text AS schema_owner
  FROM pg_namespace
 WHERE nspname = 'public';
SQL

    PUBLIC_SCHEMA_OWNER=$(psql \
       --host="$PSQL_HOST" \
       --port="$PSQL_PORT" \
       --username="$POSTGRES_USER" \
       --dbname="$TEST_DB_NAME" \
       --tuples-only \
       --no-align \
       --quiet \
       -f - < "$TMP_SQL_FILE")

    if [ "$PUBLIC_SCHEMA_OWNER" != "$TEST_DB_USER" ]; then
       fail "Existing public schema owner is unexpected; refusing to transfer ownership"
    fi
else
    cat > "$TMP_SQL_FILE" <<SQL
DO \$\$
DECLARE
schema_owner text;
BEGIN
SELECT r.rolname INTO schema_owner
     FROM pg_namespace n
     JOIN pg_roles r ON r.oid = n.nspowner
 WHERE n.nspname = 'public';

IF schema_owner IS NOT NULL
      AND schema_owner NOT IN ($(escape_sql_literal "$TEST_DB_USER"), 'pg_database_owner') THEN
       RAISE EXCEPTION 'Newly created public schema has unexpected owner';
END IF;
END \$\$;
SQL

    psql \
       --host="$PSQL_HOST" \
       --port="$PSQL_PORT" \
       --username="$POSTGRES_USER" \
       --dbname="$TEST_DB_NAME" \
       --set=ON_ERROR_STOP=1 \
       -f - < "$TMP_SQL_FILE"
fi

cat > "$TMP_SQL_FILE" <<SQL
SELECT format('ALTER SCHEMA public OWNER TO %I', $(escape_sql_literal "$TEST_DB_USER")) \gexec
SQL

psql \
    --host="$PSQL_HOST" \
    --port="$PSQL_PORT" \
    --username="$POSTGRES_USER" \
    --dbname="$TEST_DB_NAME" \
    --set=ON_ERROR_STOP=1 \
    -f - < "$TMP_SQL_FILE"

cat > "$TMP_SQL_FILE" <<SQL
DO \$\$
DECLARE
    schema_owner text;
BEGIN
    SELECT r.rolname INTO schema_owner
     FROM pg_namespace n
     JOIN pg_roles r ON r.oid = n.nspowner
     WHERE n.nspname = 'public';

    IF schema_owner IS NULL OR schema_owner <> $(escape_sql_literal "$TEST_DB_USER") THEN
       RAISE EXCEPTION 'Public schema ownership is incorrect';
    END IF;
END \$\$;
SQL

psql \
    --host="$PSQL_HOST" \
    --port="$PSQL_PORT" \
    --username="$POSTGRES_USER" \
    --dbname="$TEST_DB_NAME" \
    --set=ON_ERROR_STOP=1 \
    -f - < "$TMP_SQL_FILE"

cat > "$TMP_SQL_FILE" <<SQL
DO \$\$
DECLARE
    role_rec record;
    member_count integer;
    target_owner text;
    extra integer;
BEGIN
    SELECT rolname, rolcanlogin, rolinherit, rolsuper, rolcreatedb, rolcreaterole, rolreplication, rolbypassrls
     INTO role_rec
     FROM pg_roles
     WHERE rolname = $(escape_sql_literal "$TEST_DB_USER");

    IF role_rec.rolname IS NULL THEN
       RAISE EXCEPTION 'Test role missing after provisioning';
    END IF;
    IF role_rec.rolsuper OR role_rec.rolcreatedb OR role_rec.rolcreaterole OR role_rec.rolreplication OR role_rec.rolbypassrls THEN
       RAISE EXCEPTION 'Test role has unexpected administrative privileges';
    END IF;
    IF NOT role_rec.rolcanlogin OR role_rec.rolinherit THEN
       RAISE EXCEPTION 'Test role attributes do not match the required restricted model';
    END IF;

    SELECT COUNT(*) INTO member_count
     FROM pg_auth_members m
     JOIN pg_roles r ON r.oid = m.member
     WHERE r.rolname = $(escape_sql_literal "$TEST_DB_USER");
    IF member_count > 0 THEN
       RAISE EXCEPTION 'Test role still has direct memberships';
    END IF;

    SELECT r.rolname INTO target_owner
     FROM pg_database d
     JOIN pg_roles r ON r.oid = d.datdba
     WHERE d.datname = $(escape_sql_literal "$TEST_DB_NAME");
    IF target_owner IS NULL OR target_owner <> $(escape_sql_literal "$TEST_DB_USER") THEN
       RAISE EXCEPTION 'Target database ownership is incorrect';
    END IF;

    SELECT COUNT(*) INTO extra
     FROM pg_database d
     JOIN pg_roles r ON r.oid = d.datdba
     WHERE r.rolname = $(escape_sql_literal "$TEST_DB_USER")
      AND d.datname <> $(escape_sql_literal "$TEST_DB_NAME");
    IF extra > 0 THEN
       RAISE EXCEPTION 'Test role owns unrelated databases';
    END IF;
END \$\$;
SQL

psql \
    --host="$PSQL_HOST" \
    --port="$PSQL_PORT" \
    --username="$POSTGRES_USER" \
    --dbname="$POSTGRES_DB" \
    --set=ON_ERROR_STOP=1 \
    -f - < "$TMP_SQL_FILE"

cat > "$TMP_SQL_FILE" <<SQL
DO \$\$
DECLARE
    unexpected record;
BEGIN
    SELECT n.nspname, c.relname
     INTO unexpected
     FROM pg_class c
     JOIN pg_namespace n ON n.oid = c.relnamespace
     JOIN pg_roles r ON r.oid = c.relowner
     WHERE n.nspname = 'public'
      AND c.relkind IN ('r', 'p', 'S', 'v', 'm', 'f')
      AND r.rolname <> $(escape_sql_literal "$TEST_DB_USER")
     ORDER BY n.nspname, c.relname
     LIMIT 1;

    IF unexpected.relname IS NOT NULL THEN
       RAISE EXCEPTION 'Unexpected object ownership remains in public schema';
    END IF;
END \$\$;
SQL

psql \
    --host="$PSQL_HOST" \
    --port="$PSQL_PORT" \
    --username="$POSTGRES_USER" \
    --dbname="$TEST_DB_NAME" \
    --set=ON_ERROR_STOP=1 \
    -f - < "$TMP_SQL_FILE"

log "Dedicated PostgreSQL integration-test database provisioning completed successfully."
