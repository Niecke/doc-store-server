#!/bin/bash
set -e

echo "Starting DocStore API..."

# Test DB via Flask-Migrate (self-healing)
echo "Testing database connection..."
until flask db current; do
  echo "Database not ready - waiting..."
  sleep 5
done

# Run migrations
echo "Running database migrations..."
flask db upgrade
echo "Migrations complete!"

# Start Gunicorn
# TODO remove reload for prod run
echo "Starting Gunicorn..."
exec gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 1 \
  --reload \
  --reload-engine poll \
  --log-level info \
  "main:create_app()"