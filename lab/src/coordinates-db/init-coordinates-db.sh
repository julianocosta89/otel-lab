#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE IF NOT EXISTS coordinates (
        city TEXT,
        country TEXT,
        latitude TEXT NOT NULL,
        longitude TEXT NOT NULL,
        PRIMARY KEY (latitude, longitude)
    );
EOSQL
