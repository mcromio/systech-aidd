#!/bin/sh
# Entrypoint скрипт для API сервиса
# Применяет миграции БД перед запуском сервера

set -e

echo "=== API Container Starting ==="
echo "Waiting for PostgreSQL to be ready..."

# Ждем доступности PostgreSQL (можно улучшить в будущем)
sleep 5

echo "Running database migrations..."
alembic upgrade head

echo "Migrations completed successfully!"
echo "Starting API server..."

# Передаем управление CMD из Dockerfile
exec "$@"

