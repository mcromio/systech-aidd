# LLM Assistant Telegram Bot

Интеллектуальный Telegram-бот с персистентным хранилищем диалогов, поддержкой инструментов (Wikipedia, DateTime, WebSearch) и системой ролей.

## Возможности

✅ **Персистентное хранилище** (S1)
- История диалогов сохраняется в PostgreSQL
- Soft delete стратегия
- Автоматическое сохранение метаданных (created_at, content_length)

✅ **Интеграция с LLM**
- OpenAI API (GPT-4o-mini и другие модели)
- Function calling для инструментов
- Настраиваемый системный промпт

✅ **Инструменты (Tools)**
- 📚 Wikipedia - поиск фактической информации
- 🕐 DateTime - текущие дата и время
- 🔍 WebSearch - поиск в интернете (DuckDuckGo)

✅ **Система ролей**
- Загрузка промптов из файлов
- Готовые роли: AI Assistant, IT Consultant, Python Tutor
- Команда `/role` для просмотра активной роли

✅ **Команды бота**
- `/start` - приветствие
- `/help` - справка
- `/role` - информация о роли бота
- `/reset` - очистка истории (soft delete)

✅ **Качество кода**
- Type hints везде (mypy)
- Coverage ≥ 85%
- Ruff линтер + форматтер
- Докстринги на русском

## Технологии

- **Python 3.12**
- **aiogram 3.x** - Telegram Bot API
- **OpenAI API** - LLM интеграция
- **PostgreSQL 17** - персистентное хранилище
- **SQLAlchemy 2.0** - async ORM
- **Alembic** - миграции БД
- **uv** - управление зависимостями
- **Docker** - контейнеризация БД

## Быстрый старт

### 1. Установка зависимостей

```bash
# Клонировать репозиторий
git clone <repo-url>
cd systech-aidd_mcr

# Установить зависимости
uv sync
```

### 2. Настройка окружения

Создать `.env` файл:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_PROXY_URL=https://api.your-proxy.com/v1
OPENAI_MODEL=gpt-4o-mini

# Database (S1)
DATABASE_URL=postgresql+asyncpg://llm_user:llm_password_dev@localhost:5432/llm_assistant
POSTGRES_DB=llm_assistant
POSTGRES_USER=llm_user
POSTGRES_PASSWORD=llm_password_dev

# Bot Configuration
SYSTEM_PROMPT_FILE=prompts/default.txt
ROLE_NAME=AI Assistant
ROLE_DESCRIPTION=Универсальный ИИ-ассистент
MAX_CONTEXT_MESSAGES=10
LOG_LEVEL=INFO
```

### 3. Запуск БД

```bash
# Запустить PostgreSQL в Docker
make db-up

# Применить миграции
make db-migrate
```

### 4. Запуск бота

```bash
# Запустить бота
make run
```

## Makefile команды

### Основные

```bash
make help           # Показать все команды
make run            # Запустить бота
make test           # Запустить тесты
make lint           # Проверить код
make format         # Отформатировать код
make type-check     # Проверка типов (mypy)
make clean          # Очистить временные файлы
```

### База данных

```bash
make db-up          # Запустить PostgreSQL
make db-down        # Остановить PostgreSQL
make db-migrate     # Применить миграции
make db-rollback    # Откатить последнюю миграцию
make db-shell       # Подключиться к psql
make db-init        # Полная инициализация (up + migrate)
make db-logs        # Просмотр логов PostgreSQL
```

Подробнее: [Работа с БД](docs/database_operations.md)

### PgAdmin (опционально)

```bash
make pgadmin-up     # Запустить PgAdmin (http://localhost:5050)
make pgadmin-down   # Остановить PgAdmin
```

## Структура проекта

```
systech-aidd_mcr/
├── src/                    # Исходный код
│   ├── main.py            # Точка входа
│   ├── config.py          # Конфигурация
│   ├── bot.py             # Telegram Bot setup
│   ├── handlers.py        # Обработчики команд
│   ├── context_manager.py # Управление историей (с БД)
│   ├── llm_client.py      # LLM фасад
│   ├── db/                # База данных (S1)
│   │   ├── models.py      # SQLAlchemy модели
│   │   ├── engine.py      # Engine и session factory
│   │   ├── repositories/  # Repository pattern
│   │   │   ├── user_repository.py
│   │   │   └── message_repository.py
│   │   └── ...
│   ├── llm/               # LLM компоненты
│   │   ├── client.py      # OpenAI client
│   │   └── orchestrator.py # Tool calling
│   └── tools/             # Инструменты
│       ├── base.py        # Tool Protocol
│       ├── wikipedia.py
│       ├── datetime.py
│       └── websearch.py
│
├── prompts/               # Системные промпты для ролей
│   ├── default.txt
│   ├── it_consultant.txt
│   └── python_tutor.txt
│
├── alembic/               # Миграции БД
│   ├── versions/
│   └── env.py
│
├── tests/                 # Тесты
│   ├── test_*.py
│   └── conftest.py
│
├── docs/                  # Документация
│   ├── database_schema.md
│   ├── database_operations.md
│   ├── adr/              # Architecture Decision Records
│   └── guides/
│
├── docker-compose.dev.yml # Docker Compose для разработки
├── alembic.ini           # Конфигурация Alembic
├── pyproject.toml        # Зависимости и настройки
├── Makefile              # Команды для разработки
└── README.md             # Этот файл
```

## Разработка

### Установка dev зависимостей

```bash
uv sync  # Устанавливает всё включая dev зависимости
```

### Запуск тестов

```bash
# Все тесты с coverage
make test

# Быстрые тесты без coverage
make test-quick

# Конкретный тест
uv run pytest tests/test_context_manager.py -v
```

### Проверка кода

```bash
# Линтер
make lint

# Проверка типов
make type-check

# Форматирование
make format

# Всё сразу
make check  # lint + type-check + test
```

### Работа с миграциями

```bash
# Создать новую миграцию (автогенерация)
make db-revision

# Или вручную
uv run alembic revision --autogenerate -m "Add new field"

# Применить
make db-migrate

# Откатить
make db-rollback

# История
uv run alembic history
```

## Архитектура

### Поток данных

```
User (Telegram)
    ↓
[TelegramBot] - aiogram Bot + Dispatcher
    ↓
[MessageHandler] - обработка команд и сообщений
    ↓ ↑
    ↓ [Config] - конфигурация + системный промпт
    ↓
[ContextManager] - история диалогов (PostgreSQL)
    ↓
[LLMClient] - фасад для обратной совместимости
    ↓
[ToolOrchestrator] - tool calling loop
    ↓
[OpenAIClient] → OpenAI API
    ↓
[Tools: Wikipedia, DateTime, WebSearch]
    ↓
Response → User
```

### База данных (S1)

**Таблицы:**
- `users` - пользователи Telegram
- `messages` - сообщения диалогов (с soft delete)

**Стратегия:**
- Soft delete (is_deleted=TRUE вместо DELETE)
- Автоматическое заполнение created_at, content_length
- Индексы для быстрого поиска истории

Подробнее: [Схема БД](docs/database_schema.md)

## Конфигурация

Все настройки через переменные окружения (.env):

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | - |
| `OPENAI_API_KEY` | API ключ OpenAI | - |
| `OPENAI_PROXY_URL` | URL прокси для OpenAI | - |
| `OPENAI_MODEL` | Модель LLM | gpt-4o-mini |
| `DATABASE_URL` | PostgreSQL connection URL | postgresql+asyncpg://... |
| `SYSTEM_PROMPT_FILE` | Путь к промпту | prompts/default.txt |
| `ROLE_NAME` | Название роли | AI Assistant |
| `MAX_CONTEXT_MESSAGES` | Макс. сообщений в истории | 10 |
| `LOG_LEVEL` | Уровень логирования | INFO |

## Документация

- [📚 Guides](docs/guides/) - детальные руководства
- [🗄️ Схема БД](docs/database_schema.md) - структура таблиц
- [⚙️ Работа с БД](docs/database_operations.md) - команды и примеры
- [🏗️ ADR](docs/adr/) - архитектурные решения
- [🗺️ Roadmap](docs/roadmap.md) - план развития проекта

## Troubleshooting

### Бот не запускается

```bash
# Проверить логи
make run

# Проверить конфигурацию
cat .env

# Проверить БД
make db-logs
```

### БД не подключается

```bash
# Проверить что PostgreSQL запущен
docker ps | grep postgres

# Перезапустить БД
make db-restart

# Проверить подключение
make db-shell
```

### Ошибки миграций

```bash
# Проверить текущую версию
uv run alembic current

# Откатить и накатить заново
make db-reset  # ВНИМАНИЕ: удаляет данные!
```

Подробнее: [Troubleshooting БД](docs/database_operations.md#troubleshooting)

## Roadmap

- [x] **S0**: MVP + Technical Debt (✅ Завершен)
- [x] **S1**: Персистентное хранение (PostgreSQL + SQLAlchemy + Alembic) ✅
- [ ] **S2**: Production Ready (Docker, CI/CD, мониторинг)
- [ ] **S3**: Расширенные возможности (голос, изображения, новые tools)
- [ ] **S4**: Multi-bot Framework

Подробнее: [Roadmap](docs/roadmap.md)

## Метрики качества

| Метрика | Значение |
|---------|----------|
| Test Coverage | ≥ 85% |
| Tests Passed | 72/72 (100%) |
| Линтер | 0 ошибок (ruff + mypy) |
| Архитектура | SOLID + DRY + Type Safety |
| Documentation | 100% (все публичные методы) |

## Лицензия

MIT

## Авторы

Development Team

---

**Версия**: 0.1.0 (S1: Persistent Storage)
**Последнее обновление**: 16 октября 2025

