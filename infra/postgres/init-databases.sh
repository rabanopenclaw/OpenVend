#!/usr/bin/env sh
set -eu

databases="
kratos
authorization_adapter
contacts
inventory
orders
reporting
export
"

for database in $databases; do
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<SQL
SELECT 'CREATE DATABASE $database'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$database')\gexec
SQL
done
