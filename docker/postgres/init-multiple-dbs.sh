#!/bin/sh
set -e

if [ -n "$TEST_POSTGRES_DB" ]; then
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE $TEST_POSTGRES_DB;
EOSQL
fi
