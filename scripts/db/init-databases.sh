#!/bin/sh
# Runs once when the local dev PostgreSQL container is first created.
# Creates the dev database (POSTGRES_DB) and a separate database for tests.
set -eu
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<SQL
CREATE DATABASE goldscope_test OWNER "$POSTGRES_USER";
SQL
