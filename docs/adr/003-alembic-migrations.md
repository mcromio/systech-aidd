# ADR-003: Использование Alembic для миграций БД

**Дата**: 16 октября 2025
**Статус**: Принято
**Авторы**: Development Team

## Контекст

При работе с базой данных необходима система управления изменениями схемы (миграции). Схема БД будет эволюционировать от спринта к спринту, и нужен надежный механизм версионирования этих изменений.

## Рассматриваемые варианты

### 1. Ручные SQL скрипты
**Плюсы:**
- Максимальная простота (KISS)
- Полный контроль над SQL
- Нет зависимостей
- Прозрачность

**Минусы:**
- Ручное отслеживание версий
- Нужно писать up и down миграции вручную
- Риск human error
- Нет автогенерации из моделей
- Сложно синхронизировать модели и схему

### 2. Alembic
**Плюсы:**
- Официальный инструмент для SQLAlchemy
- Автогенерация миграций из моделей
- Версионирование (up/down)
- История миграций в коде
- Интеграция с SQLAlchemy
- Команды `upgrade`, `downgrade`, `history`

**Минусы:**
- Дополнительная зависимость
- Требует настройки (alembic.ini, env.py)
- Автогенерация может быть неточной
- Нужно знать Alembic DSL

### 3. Django-like встроенные миграции (Tortoise ORM)
**Плюсы:**
- Интегрировано с ORM
- Проще настройка

**Минусы:**
- Привязка к конкретному ORM (не SQLAlchemy)
- Меньшая гибкость

### 4. Без миграций (создание схемы через Base.metadata.create_all)
**Плюсы:**
- Максимальная простота
- Нет дополнительных инструментов

**Минусы:**
- ❌ Нет версионирования изменений
- ❌ Невозможно откатить изменения
- ❌ Проблемы при изменении схемы в production
- ❌ Нет истории изменений

## Решение

**Выбран Alembic**

## Обоснование

1. **Версионирование схемы**: Каждое изменение - отдельная миграция с timestamp
   ```
   alembic/versions/
   ├── 001_20251016_1200_initial_schema.py
   ├── 002_20251020_1400_add_is_deleted.py
   └── 003_20251025_0900_add_indexes.py
   ```

2. **Автогенерация**: Изменил модель → получил миграцию
   ```bash
   # Изменили Message модель
   alembic revision --autogenerate -m "Add content_length field"
   # Получили готовую миграцию
   ```

3. **Up/Down миграции**: Можно откатиться к любой версии
   ```bash
   alembic upgrade head        # применить все
   alembic downgrade -1        # откатить последнюю
   alembic downgrade base      # откатить все
   ```

4. **История изменений**: Видим всю эволюцию схемы
   ```bash
   alembic history
   alembic current
   ```

5. **Branching и merging**: Поддержка multiple branches (для команд)

6. **Интеграция с SQLAlchemy**: Работает с нашими моделями напрямую

7. **Production-ready**:
   - Автоматическая проверка версии при старте
   - Возможность автоприменения миграций при deploy
   - Логирование всех изменений

8. **CI/CD**: Легко интегрируется в pipeline
   ```yaml
   - run: alembic upgrade head
   - run: pytest
   ```

## Структура миграций

```
systech-aidd_mcr/
├── alembic/
│   ├── versions/           # Миграции
│   │   ├── 001_initial_schema.py
│   │   └── ...
│   ├── env.py             # Настройка Alembic
│   ├── script.py.mako     # Шаблон миграций
│   └── README
├── alembic.ini            # Конфигурация
└── src/db/
    ├── base.py            # Base для моделей
    └── models.py          # SQLAlchemy модели
```

## Workflow

### 1. Создание новой миграции

```bash
# Автогенерация из изменений в моделях
alembic revision --autogenerate -m "Add is_deleted to messages"

# Ручное создание (для data migrations)
alembic revision -m "Migrate old data format"
```

### 2. Проверка миграции

```python
# alembic/versions/xxx_add_is_deleted.py
def upgrade():
    op.add_column('messages',
                  sa.Column('is_deleted', sa.Boolean(),
                            nullable=False, server_default='false'))

def downgrade():
    op.drop_column('messages', 'is_deleted')
```

### 3. Применение миграции

```bash
# Локально
alembic upgrade head

# В Docker
docker-compose exec app alembic upgrade head

# Через Makefile
make db-migrate
```

### 4. Откат (если что-то пошло не так)

```bash
alembic downgrade -1
```

## Последствия

### Положительные
- ✅ Полная история изменений схемы БД
- ✅ Возможность отката в любой момент
- ✅ Автогенерация миграций (экономия времени)
- ✅ Синхронизация моделей и схемы БД
- ✅ Готовность к production deployment
- ✅ Командная работа (merge миграций)

### Отрицательные
- ⚠️ Дополнительная зависимость (alembic)
- ⚠️ Требует настройки (alembic.ini, env.py)
- ⚠️ Нужно проверять автогенерированные миграции

### Риски и митигации

- **Риск**: Автогенерация создает неправильную миграцию
  **Митигация**:
  - Всегда проверять миграции перед коммитом
  - Тестировать up/down в dev окружении
  - Code review миграций

- **Риск**: Конфликты миграций при командной работе
  **Митигация**:
  - Регулярная синхронизация с main branch
  - Alembic поддерживает merge миграций
  - Документирование процесса в workflow

- **Риск**: Потеря данных при downgrade
  **Митигация**:
  - Бэкапы перед миграциями в production
  - Тестирование миграций на staging
  - Data migrations для сложных изменений

## Best Practices

1. **Всегда проверять автогенерацию**:
   ```bash
   alembic revision --autogenerate -m "..."
   # Открыть файл миграции и проверить
   ```

2. **Осмысленные сообщения**:
   ```bash
   ✅ "Add is_deleted and deleted_at to messages"
   ❌ "Update schema"
   ```

3. **Тестировать up и down**:
   ```bash
   alembic upgrade head
   alembic downgrade -1
   alembic upgrade head
   ```

4. **Не редактировать примененные миграции**:
   - Если миграция уже в production, создавать новую
   - Исключение: исправление критических багов

5. **Data migrations отдельно**:
   ```python
   # Для изменения данных - ручная миграция
   def upgrade():
       # Изменение схемы
       op.add_column(...)

       # Миграция данных
       connection = op.get_bind()
       connection.execute(text("UPDATE messages SET ..."))
   ```

## Интеграция с разработкой

```makefile
# Makefile
db-migrate:        # Применить миграции
    alembic upgrade head

db-rollback:       # Откатить последнюю
    alembic downgrade -1

db-history:        # История миграций
    alembic history

db-current:        # Текущая версия
    alembic current

db-reset:          # Сбросить БД и накатить заново
    alembic downgrade base
    alembic upgrade head
```

## Примеры миграций

### Создание таблицы
```python
def upgrade():
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
```

### Добавление индекса
```python
def upgrade():
    op.create_index(
        'idx_messages_user_id_created_at',
        'messages',
        ['user_id', 'created_at']
    )
```

### Data migration
```python
def upgrade():
    # Добавляем колонку
    op.add_column('messages',
                  sa.Column('content_length', sa.Integer()))

    # Заполняем данные
    connection = op.get_bind()
    connection.execute(
        text("UPDATE messages SET content_length = LENGTH(content)")
    )

    # Делаем NOT NULL
    op.alter_column('messages', 'content_length', nullable=False)
```

## Ссылки

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Alembic Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html)

