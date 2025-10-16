# Быстрый старт S1: База данных

**Спринт S1** добавил персистентное хранилище истории диалогов в PostgreSQL.

## Что изменилось

✅ **До S1**: История диалогов хранилась в памяти (dict) и терялась при перезапуске
✅ **После S1**: История сохраняется в PostgreSQL и доступна после перезапуска

## Минимальная инструкция

### 1. Обновить зависимости

```bash
uv sync
```

Будут установлены:
- `sqlalchemy[asyncio]>=2.0.0`
- `alembic>=1.13.0`
- `asyncpg>=0.29.0`

### 2. Добавить в .env

Добавьте эти строки в ваш `.env` файл:

```bash
# Database Configuration (NEW in S1)
DATABASE_URL=postgresql+asyncpg://llm_user:llm_password_dev@localhost:5432/llm_assistant
POSTGRES_DB=llm_assistant
POSTGRES_USER=llm_user
POSTGRES_PASSWORD=llm_password_dev
POSTGRES_PORT=5432
DATABASE_POOL_SIZE=5
DATABASE_ECHO=false
```

### 3. Запустить PostgreSQL

```bash
make db-up
```

Это запустит PostgreSQL 17 в Docker контейнере.

### 4. Применить миграции

```bash
make db-migrate
```

Это создаст таблицы `users` и `messages` в БД.

### 5. Запустить бота

```bash
make run
```

Теперь история диалогов сохраняется в БД!

## Проверка работы

1. Отправьте боту несколько сообщений
2. Остановите бота (Ctrl+C)
3. Запустите снова (`make run`)
4. Отправьте боту сообщение - он должен помнить историю диалога!

## Просмотр данных

### Через psql

```bash
make db-shell
```

```sql
-- Посмотреть пользователей
SELECT * FROM users;

-- Посмотреть сообщения
SELECT u.telegram_id, m.role, m.content, m.created_at
FROM messages m
JOIN users u ON m.user_id = u.id
WHERE m.is_deleted = FALSE
ORDER BY m.created_at DESC
LIMIT 10;
```

### Через PgAdmin (опционально)

```bash
make pgadmin-up
```

Откройте http://localhost:5050

**Credentials:**
- Email: `admin@localhost.com`
- Password: `admin`

## Команда /reset

Команда `/reset` теперь делает **soft delete** (is_deleted=TRUE) вместо физического удаления.

Данные остаются в БД, но не показываются в истории диалога.

## Что НЕ изменилось

✅ Все команды бота работают как раньше: `/start`, `/help`, `/role`, `/reset`
✅ API компонентов не изменился (обратная совместимость)
✅ Поведение бота идентичное, только с персистентностью

## Troubleshooting

### БД не запускается

```bash
# Проверить логи
make db-logs

# Перезапустить
make db-restart

# Если не помогает - пересоздать
make db-down
docker volume rm systech-aidd_mcr_postgres_data
make db-up
make db-migrate
```

### Ошибка "connection refused"

Проверьте:
1. PostgreSQL запущен: `docker ps | grep postgres`
2. Переменные окружения: `cat .env | grep DATABASE`
3. Порт 5432 свободен: `netstat -an | grep 5432`

### Ошибка при миграции

```bash
# Проверить текущую версию
uv run alembic current

# Откатить и накатить заново (ВНИМАНИЕ: удаляет данные)
make db-reset
```

## Полезные команды

```bash
make db-up          # Запустить PostgreSQL
make db-down        # Остановить PostgreSQL
make db-migrate     # Применить миграции
make db-shell       # Подключиться к psql
make db-logs        # Логи PostgreSQL
make db-init        # Полная инициализация (up + migrate)
```

## Дополнительно

- [📚 Полная документация по БД](./database_operations.md)
- [🗄️ Схема БД](./database_schema.md)
- [🏗️ Архитектурные решения (ADR)](./adr/)
- [📖 README](../readme.md)

---

**Версия**: S1
**Дата**: 16 октября 2025

