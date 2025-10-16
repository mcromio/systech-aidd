# Схема базы данных

**Версия**: 1.0
**Дата**: 16 октября 2025
**Спринт**: S1 - Персистентное хранение данных

## Обзор

База данных хранит историю диалогов пользователей с Telegram-ботом. Используется стратегия **soft delete** для всех удалений.

## Таблицы

### 1. `users`

Хранит информацию о пользователях Telegram.

| Колонка | Тип | Описание | Constraints |
|---------|-----|----------|-------------|
| `id` | SERIAL | Внутренний ID | PRIMARY KEY |
| `telegram_id` | BIGINT | Telegram User ID | UNIQUE, NOT NULL |
| `username` | VARCHAR(255) | Telegram username | NULLABLE |
| `first_name` | VARCHAR(255) | Имя пользователя | NULLABLE |
| `last_name` | VARCHAR(255) | Фамилия пользователя | NULLABLE |
| `created_at` | TIMESTAMP WITH TIME ZONE | Дата регистрации | NOT NULL, DEFAULT NOW() |
| `last_seen_at` | TIMESTAMP WITH TIME ZONE | Последняя активность | NULLABLE |

**Индексы:**
- `PRIMARY KEY (id)`
- `UNIQUE INDEX idx_users_telegram_id (telegram_id)`

**Примечания:**
- `telegram_id` - уникальный идентификатор из Telegram API
- `username` может быть NULL (не у всех пользователей есть username)
- `last_seen_at` обновляется при каждом сообщении

### 2. `messages`

Хранит все сообщения диалогов (пользователя и ассистента).

| Колонка | Тип | Описание | Constraints |
|---------|-----|----------|-------------|
| `id` | SERIAL | Внутренний ID сообщения | PRIMARY KEY |
| `user_id` | INTEGER | ID пользователя | FOREIGN KEY → users(id), NOT NULL |
| `role` | VARCHAR(20) | Роль отправителя | CHECK IN ('user', 'assistant', 'system'), NOT NULL |
| `content` | TEXT | Содержимое сообщения | NOT NULL |
| `content_length` | INTEGER | Длина сообщения в символах | NOT NULL |
| `created_at` | TIMESTAMP WITH TIME ZONE | Дата создания | NOT NULL, DEFAULT NOW() |
| `is_deleted` | BOOLEAN | Флаг soft delete | NOT NULL, DEFAULT FALSE |
| `deleted_at` | TIMESTAMP WITH TIME ZONE | Дата удаления | NULLABLE |

**Индексы:**
- `PRIMARY KEY (id)`
- `INDEX idx_messages_user_id_created_at (user_id, created_at DESC)` - для get_history
- `INDEX idx_messages_is_deleted (is_deleted)` - для фильтрации активных
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`

**Примечания:**
- `role` может быть: 'user', 'assistant', 'system'
- `content_length` вычисляется автоматически при создании (len(content))
- `is_deleted=TRUE` означает мягкое удаление (команда /reset)
- `deleted_at` заполняется при is_deleted=TRUE

**Soft Delete стратегия:**
```sql
-- Вместо DELETE
UPDATE messages
SET is_deleted = TRUE, deleted_at = NOW()
WHERE user_id = ? AND is_deleted = FALSE;

-- При выборке всегда фильтруем
SELECT * FROM messages
WHERE user_id = ? AND is_deleted = FALSE
ORDER BY created_at DESC;
```

## Связи между таблицами

```
┌─────────────────┐
│     users       │
│─────────────────│
│ id (PK)         │
│ telegram_id (U) │◄────────┐
│ username        │         │
│ first_name      │         │
│ last_name       │         │
│ created_at      │         │
│ last_seen_at    │         │
└─────────────────┘         │
                            │ FK
                            │
                    ┌───────┴──────────┐
                    │    messages      │
                    │──────────────────│
                    │ id (PK)          │
                    │ user_id (FK)     │
                    │ role             │
                    │ content          │
                    │ content_length   │
                    │ created_at       │
                    │ is_deleted       │
                    │ deleted_at       │
                    └──────────────────┘
```

**Отношения:**
- `users` 1:N `messages` - один пользователь может иметь множество сообщений
- ON DELETE CASCADE - при удалении пользователя удаляются его сообщения

## Запросы и операции

### Создание пользователя (get_or_create)

```sql
-- Проверка существования
SELECT id FROM users WHERE telegram_id = ?;

-- Если не существует
INSERT INTO users (telegram_id, username, first_name, last_name, created_at)
VALUES (?, ?, ?, ?, NOW())
RETURNING id;

-- Обновление last_seen_at
UPDATE users SET last_seen_at = NOW() WHERE telegram_id = ?;
```

### Добавление сообщения

```sql
INSERT INTO messages (user_id, role, content, content_length, created_at)
VALUES (?, ?, ?, LENGTH(?), NOW())
RETURNING id, created_at;
```

### Получение истории диалога

```sql
SELECT id, role, content, content_length, created_at
FROM messages
WHERE user_id = ? AND is_deleted = FALSE
ORDER BY created_at DESC
LIMIT ?;
```

### Soft delete сообщений (команда /reset)

```sql
UPDATE messages
SET is_deleted = TRUE, deleted_at = NOW()
WHERE user_id = ? AND is_deleted = FALSE;
```

### Подсчет активных сообщений

```sql
SELECT COUNT(*)
FROM messages
WHERE user_id = ? AND is_deleted = FALSE;
```

## Производительность

### Оценка размера данных

**Предположения:**
- 1000 активных пользователей
- В среднем 100 сообщений на пользователя
- Средняя длина сообщения: 500 символов

**Расчет:**
```
users: 1000 * ~200 bytes = ~200 KB
messages: 1000 * 100 * ~550 bytes = ~55 MB
Total: ~55 MB
```

**С ростом до 10K пользователей:**
```
users: 10000 * ~200 bytes = ~2 MB
messages: 10000 * 100 * ~550 bytes = ~550 MB
Total: ~550 MB
```

Это очень скромные объемы для PostgreSQL.

### Индексы

**idx_messages_user_id_created_at:**
- Используется для быстрой выборки истории
- DESC сортировка для получения последних сообщений
- Composite index (user_id, created_at)

**idx_messages_is_deleted:**
- Ускоряет фильтрацию активных сообщений
- Небольшой overhead (~5% от размера таблицы)

### Планы запросов (EXPLAIN ANALYZE)

```sql
-- Получение истории (ожидаемый план)
EXPLAIN ANALYZE
SELECT * FROM messages
WHERE user_id = 1 AND is_deleted = FALSE
ORDER BY created_at DESC
LIMIT 10;

-- Ожидаемый результат:
-- Index Scan using idx_messages_user_id_created_at
-- Filter: (NOT is_deleted)
-- Execution time: < 1ms
```

## Миграции

### Версия 1 - Initial Schema (001_initial_schema.py)

Создает таблицы `users` и `messages` с базовыми полями и индексами.

```python
# alembic/versions/001_initial_schema.py
def upgrade():
    # Создание таблицы users
    op.create_table('users', ...)

    # Создание таблицы messages
    op.create_table('messages', ...)

    # Создание индексов
    op.create_index('idx_users_telegram_id', 'users', ['telegram_id'], unique=True)
    op.create_index('idx_messages_user_id_created_at', 'messages', ['user_id', 'created_at'])
    op.create_index('idx_messages_is_deleted', 'messages', ['is_deleted'])
```

## Будущие расширения

### Планируемые таблицы (S2+)

**`conversations`** - метаданные диалогов:
- session_id
- title (автогенерация из первых сообщений)
- started_at, ended_at
- message_count
- is_archived

**`user_preferences`** - настройки пользователей:
- preferred_language
- timezone
- notification_settings

**`tool_calls`** - логирование вызовов инструментов:
- tool_name
- arguments
- result
- execution_time

## Бэкапы и восстановление

### Backup стратегия

```bash
# Полный бэкап БД
pg_dump -U llm_user -d llm_assistant -F c -f backup_$(date +%Y%m%d).dump

# Восстановление
pg_restore -U llm_user -d llm_assistant backup_20251016.dump
```

### Retention policy

- Ежедневные бэкапы: 7 дней
- Еженедельные бэкапы: 4 недели
- Ежемесячные бэкапы: 12 месяцев

## Безопасность

### Права доступа

```sql
-- Создание пользователя приложения (read/write)
CREATE USER llm_app WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO llm_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO llm_app;

-- Создание пользователя только для чтения (analytics)
CREATE USER llm_reader WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO llm_reader;
```

### Шифрование

- Соединения: SSL/TLS (require в production)
- Данные в покое: PostgreSQL encryption at rest (опционально)
- Пароли: SCRAM-SHA-256 authentication

## Мониторинг

### Ключевые метрики

```sql
-- Количество пользователей
SELECT COUNT(*) FROM users;

-- Количество сообщений (активных)
SELECT COUNT(*) FROM messages WHERE is_deleted = FALSE;

-- Количество удаленных сообщений
SELECT COUNT(*) FROM messages WHERE is_deleted = TRUE;

-- Средняя длина сообщения
SELECT AVG(content_length) FROM messages WHERE is_deleted = FALSE;

-- Топ активных пользователей
SELECT user_id, COUNT(*) as message_count
FROM messages
WHERE is_deleted = FALSE
GROUP BY user_id
ORDER BY message_count DESC
LIMIT 10;

-- Размер таблиц
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Тестовые данные

```sql
-- Создание тестового пользователя
INSERT INTO users (telegram_id, username, first_name, created_at)
VALUES (123456789, 'test_user', 'Test', NOW())
RETURNING id;

-- Создание тестовых сообщений
INSERT INTO messages (user_id, role, content, content_length, created_at)
VALUES
    (1, 'user', 'Привет!', 7, NOW()),
    (1, 'assistant', 'Здравствуйте! Чем могу помочь?', 31, NOW()),
    (1, 'user', 'Какая погода?', 13, NOW());

-- Soft delete
UPDATE messages SET is_deleted = TRUE, deleted_at = NOW() WHERE user_id = 1;
```

## Ссылки

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [Soft Delete Pattern](https://en.wikipedia.org/wiki/Soft_delete)

