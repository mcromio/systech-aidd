# Работа с базой данных

**Версия**: 1.0
**Дата**: 16 октября 2025
**Спринт**: S1 - Персистентное хранение данных

## Обзор

В спринте S1 добавлено персистентное хранение истории диалогов в PostgreSQL. Используется:
- **PostgreSQL 17** в Docker
- **SQLAlchemy 2.0** ORM (async)
- **Alembic** для миграций
- **Soft delete** стратегия

## Быстрый старт

### 1. Запуск БД

```bash
# Запустить PostgreSQL в Docker
make db-up

# Или вручную
docker-compose -f docker-compose.dev.yml up -d postgres
```

### 2. Применение миграций

```bash
# Применить все миграции
make db-migrate

# Или вручную
uv run alembic upgrade head
```

### 3. Запуск приложения

```bash
# Запустить бота
make run
```

### 4. Остановка БД

```bash
# Остановить PostgreSQL
make db-down
```

## Makefile команды

### Основные команды

```bash
make db-up          # Запустить PostgreSQL в Docker
make db-down        # Остановить PostgreSQL
make db-logs        # Просмотр логов PostgreSQL
make db-shell       # Подключиться к psql
```

### Миграции

```bash
make db-migrate     # Применить все миграции
make db-rollback    # Откатить последнюю миграцию
make db-history     # Просмотр истории миграций
make db-current     # Текущая версия БД
make db-reset       # Сбросить БД (ВНИМАНИЕ: удаляет все данные)
make db-revision    # Создать новую миграцию (автогенерация)
```

### Комбинированные команды

```bash
make db-init        # db-up + db-migrate (полная инициализация)
make db-restart     # db-down + db-up (перезапуск)
```

### PgAdmin (опционально)

```bash
make pgadmin-up     # Запустить PgAdmin (http://localhost:5050)
make pgadmin-down   # Остановить PgAdmin
```

**Credentials для PgAdmin:**
- Email: `admin@localhost.com`
- Password: `admin`

## Alembic команды

### Просмотр статуса

```bash
# Текущая версия схемы БД
alembic current

# История всех миграций
alembic history

# Подробная история с номерами ревизий
alembic history --verbose
```

### Применение миграций

```bash
# Применить все миграции
alembic upgrade head

# Применить одну миграцию вперёд
alembic upgrade +1

# Применить до конкретной ревизии
alembic upgrade <revision_id>

# Показать SQL без применения
alembic upgrade head --sql
```

### Откат миграций

```bash
# Откатить одну миграцию назад
alembic downgrade -1

# Откатить до конкретной ревизии
alembic downgrade <revision_id>

# Откатить все миграции
alembic downgrade base

# Показать SQL отката без применения
alembic downgrade -1 --sql
```

### Создание миграций

```bash
# Автогенерация миграции из изменений моделей
alembic revision --autogenerate -m "Описание изменений"

# Создание пустой миграции (для data migrations)
alembic revision -m "Описание изменений"
```

**ВАЖНО**: Всегда проверяйте автогенерированные миграции перед коммитом!

## Подключение к БД

### psql (из контейнера)

```bash
# Через Makefile
make db-shell

# Или вручную
docker-compose -f docker-compose.dev.yml exec postgres psql -U llm_user -d llm_assistant
```

### PgAdmin (веб-интерфейс)

```bash
# Запустить PgAdmin
make pgadmin-up

# Открыть http://localhost:5050
# Email: admin@localhost.com
# Password: admin
```

**Настройка подключения в PgAdmin:**
1. Add New Server
2. Name: LLM Assistant
3. Connection:
   - Host: `postgres` (имя сервиса в Docker)
   - Port: `5432`
   - Database: `llm_assistant`
   - Username: `llm_user`
   - Password: `llm_password_dev`

### Python (программно)

```python
from src.config import Config
from src.db.engine import create_engine, get_session_factory
from src.db.session import get_session
from src.db.repositories import UserRepository, MessageRepository

# Создание engine
config = Config()
engine = create_engine(config)
session_factory = get_session_factory(engine)

# Использование репозиториев
async with get_session(session_factory) as session:
    user_repo = UserRepository(session)
    message_repo = MessageRepository(session)

    # Получить или создать пользователя
    user, created = await user_repo.get_or_create_user(
        telegram_id=123456789,
        username="test_user"
    )

    # Создать сообщение
    message = await message_repo.create_message(
        user_id=user.id,
        role="user",
        content="Привет!"
    )

    # Получить историю
    history = await message_repo.get_user_history(
        user_id=user.id,
        limit=10
    )
```

## Полезные SQL запросы

### Просмотр данных

```sql
-- Все пользователи
SELECT id, telegram_id, username, created_at, last_seen_at
FROM users
ORDER BY created_at DESC;

-- Все активные сообщения
SELECT m.id, u.telegram_id, m.role, LEFT(m.content, 50) as content_preview,
       m.content_length, m.created_at
FROM messages m
JOIN users u ON m.user_id = u.id
WHERE m.is_deleted = FALSE
ORDER BY m.created_at DESC
LIMIT 20;

-- Статистика по пользователям
SELECT
    u.telegram_id,
    u.username,
    COUNT(m.id) as total_messages,
    SUM(CASE WHEN m.is_deleted THEN 1 ELSE 0 END) as deleted_messages,
    AVG(m.content_length) as avg_message_length,
    MAX(m.created_at) as last_message_at
FROM users u
LEFT JOIN messages m ON u.id = m.user_id
GROUP BY u.id, u.telegram_id, u.username
ORDER BY total_messages DESC;
```

### Управление данными

```sql
-- Soft delete всех сообщений пользователя
UPDATE messages
SET is_deleted = TRUE, deleted_at = NOW()
WHERE user_id = (SELECT id FROM users WHERE telegram_id = 123456789)
  AND is_deleted = FALSE;

-- Восстановление удалённых сообщений
UPDATE messages
SET is_deleted = FALSE, deleted_at = NULL
WHERE user_id = (SELECT id FROM users WHERE telegram_id = 123456789)
  AND is_deleted = TRUE;

-- Физическое удаление старых soft-deleted сообщений (>30 дней)
DELETE FROM messages
WHERE is_deleted = TRUE
  AND deleted_at < NOW() - INTERVAL '30 days';
```

### Мониторинг

```sql
-- Размер таблиц
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;

-- Количество записей
SELECT
    'users' as table_name,
    COUNT(*) as count
FROM users
UNION ALL
SELECT
    'messages (active)' as table_name,
    COUNT(*) as count
FROM messages
WHERE is_deleted = FALSE
UNION ALL
SELECT
    'messages (deleted)' as table_name,
    COUNT(*) as count
FROM messages
WHERE is_deleted = TRUE;

-- Активность по дням
SELECT
    DATE(created_at) as date,
    COUNT(*) as messages_count,
    COUNT(DISTINCT user_id) as unique_users
FROM messages
WHERE is_deleted = FALSE
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 30;
```

## Backup и восстановление

### Создание backup

```bash
# Full backup
docker-compose -f docker-compose.dev.yml exec postgres pg_dump \
  -U llm_user -d llm_assistant -F c -f /tmp/backup_$(date +%Y%m%d).dump

# Скопировать backup из контейнера
docker cp llm-assistant-db:/tmp/backup_$(date +%Y%m%d).dump ./backups/

# Только схема (без данных)
docker-compose -f docker-compose.dev.yml exec postgres pg_dump \
  -U llm_user -d llm_assistant --schema-only > schema.sql

# Только данные
docker-compose -f docker-compose.dev.yml exec postgres pg_dump \
  -U llm_user -d llm_assistant --data-only > data.sql
```

### Восстановление из backup

```bash
# Восстановление full backup
docker cp ./backups/backup_20251016.dump llm-assistant-db:/tmp/
docker-compose -f docker-compose.dev.yml exec postgres pg_restore \
  -U llm_user -d llm_assistant -c /tmp/backup_20251016.dump

# Восстановление из SQL файла
cat schema.sql | docker-compose -f docker-compose.dev.yml exec -T postgres \
  psql -U llm_user -d llm_assistant
```

## Troubleshooting

### БД не запускается

```bash
# Проверить логи
make db-logs

# Проверить статус контейнера
docker ps -a | grep postgres

# Перезапустить
make db-restart

# Если не помогает - пересоздать
make db-down
docker volume rm systech-aidd_mcr_postgres_data
make db-up
make db-migrate
```

### Миграции не применяются

```bash
# Проверить текущую версию
alembic current

# Проверить историю
alembic history

# Если БД пустая - применить с нуля
alembic upgrade head

# Если есть конфликты - откатить и накатить заново
alembic downgrade base
alembic upgrade head
```

### Connection refused

```bash
# Проверить что БД запущена
docker ps | grep postgres

# Проверить порт
netstat -an | grep 5432

# Проверить переменные окружения
cat .env | grep DATABASE

# Проверить подключение вручную
docker-compose -f docker-compose.dev.yml exec postgres \
  psql -U llm_user -d llm_assistant -c "SELECT 1;"
```

### Медленные запросы

```sql
-- Включить логирование медленных запросов (>100ms)
ALTER DATABASE llm_assistant SET log_min_duration_statement = 100;

-- Посмотреть статистику по таблицам
SELECT * FROM pg_stat_user_tables WHERE schemaname = 'public';

-- EXPLAIN ANALYZE для проблемного запроса
EXPLAIN ANALYZE
SELECT * FROM messages
WHERE user_id = 1 AND is_deleted = FALSE
ORDER BY created_at DESC
LIMIT 10;

-- Проверить индексы
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

## Best Practices

### 1. Всегда делать backup перед миграциями в production

```bash
# Production workflow
make db-backup
alembic upgrade head
# Если что-то пошло не так
alembic downgrade -1
make db-restore
```

### 2. Проверять автогенерацию миграций

```bash
# Создать миграцию
alembic revision --autogenerate -m "Add field"

# ОБЯЗАТЕЛЬНО проверить файл миграции
cat alembic/versions/<timestamp>_add_field.py

# Тестировать up и down
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

### 3. Не редактировать примененные миграции

Если миграция уже применена в production - создавать новую миграцию для исправления.

### 4. Использовать транзакции

```python
async with get_session(session_factory) as session:
    try:
        # Все операции в одной транзакции
        user = await user_repo.create(...)
        message = await message_repo.create(...)
        # Автоматический commit при выходе из context manager
    except Exception:
        # Автоматический rollback при ошибке
        raise
```

### 5. Мониторить размер БД

```bash
# Еженедельно проверять размер
SELECT pg_size_pretty(pg_database_size('llm_assistant'));

# Очищать старые soft-deleted записи
DELETE FROM messages
WHERE is_deleted = TRUE
  AND deleted_at < NOW() - INTERVAL '90 days';
```

## Ссылки

- [PostgreSQL Documentation](https://www.postgresql.org/docs/17/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Схема БД](./database_schema.md)
- [ER-диаграмма](./er_diagram.txt)

