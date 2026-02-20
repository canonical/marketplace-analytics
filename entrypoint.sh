#!/bin/sh
set -e

echo "Running database migrations..."
python migrate.py
echo "Migrations complete."

exec flask run --host=0.0.0.0 --port=8080
