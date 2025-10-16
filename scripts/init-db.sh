#!/bin/bash
set -e

# Инициализация БД для разработки
# Этот скрипт выполняется при первом запуске PostgreSQL контейнера

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Создание расширений (если понадобятся в будущем)
    -- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    -- CREATE EXTENSION IF NOT EXISTS "pg_trgm";

    -- Установка часового пояса по умолчанию
    ALTER DATABASE $POSTGRES_DB SET timezone TO 'UTC';

    -- Логирование
    \echo '✅ Database initialized successfully'
EOSQL

