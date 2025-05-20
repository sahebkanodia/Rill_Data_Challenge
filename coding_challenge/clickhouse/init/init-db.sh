#!/bin/bash
set -e

# Wait for ClickHouse to be ready
until clickhouse-client --host localhost --query "SELECT 1" >/dev/null 2>&1; do
    echo "Waiting for ClickHouse to start..."
    sleep 1
done

echo "ClickHouse is up - executing init script"

# Execute the SQL file
clickhouse-client --host localhost --multiquery < /docker-entrypoint-initdb.d/01_init.sql

echo "Initialization complete" 