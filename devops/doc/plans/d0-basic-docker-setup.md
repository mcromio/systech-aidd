# Спринт D0: Basic Docker Setup - План реализации

> **Дата создания:** 18.10.2025
> **Дата завершения:** 18.10.2025, 10:46
> **Статус:** ✅ **COMPLETED - ALL 4 SERVICES WORKING!**
> **Фокус:** MVP - простота и скорость, без сложных оптимизаций

**Отчеты о тестировании:**
- [d0-testing-report.md](../reports/d0-testing-report.md) - промежуточный
- [d0-testing-report-final.md](../reports/d0-testing-report-final.md) - ✅ **финальный (все работает!)**

## Цель
Запустить все сервисы локально через `docker-compose up` одной командой.

## Файлы для создания/модификации

### 1. Dockerfile для Bot
**Файл:** `Dockerfile.bot`

Простой MVP Dockerfile на основе `python:3.12-alpine`:
- Установить зависимости (curl для healthcheck)
- Скопировать pyproject.toml, uv.lock
- Установить зависимости через `pip install -e .`
- Скопировать весь код
- CMD: `python -m src.main`

Особенности:
- Alpine образ (~50MB вместо 300MB+)
- Одна стадия сборки (MVP, без multi-stage)
- Простой healthcheck

### 2. Dockerfile для API
**Файл:** `Dockerfile.api`

Аналогичен Bot Dockerfile:
- `python:3.12-alpine`
- Скопировать entrypoint-api.sh
- **RUN chmod +x entrypoint-api.sh** (сделать executable)
- ENTRYPOINT: `./entrypoint-api.sh`
- CMD: `uvicorn src.api.router:app --host 0.0.0.0 --port 8000`

### 2.1. Entrypoint скрипт для API
**Файл:** `entrypoint-api.sh`

Bash скрипт для применения миграций перед запуском API:
```bash
#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting API server..."
exec "$@"
```

Этот скрипт выполнит миграции Alembic при первом запуске API контейнера.

### 3. Dockerfile для Frontend
**Файл:** `Dockerfile.frontend` (в корне проекта)

На основе `node:22-alpine`:
- Установить pnpm глобально
- Скопировать `package.json`, `pnpm-lock.yaml`
- `pnpm install --frozen-lockfile`
- Скопировать весь код
- `pnpm build`
- CMD: `pnpm start` (production mode)

**Build context:** `./frontend/app` (в docker-compose.yml)

### 4. docker-compose.yml (новый)
**Файл:** `docker-compose.yml`

Объединить существующий `docker-compose.dev.yml` + новые сервисы:

**Сервисы:**
- `postgres`: из docker-compose.dev.yml, порт 5432
- `bot`: build context=., dockerfile=Dockerfile.bot, depends_on: postgres
- `api`: build context=., dockerfile=Dockerfile.api, порт 8000, depends_on: postgres
- `frontend`: build context=./frontend/app, dockerfile=../../Dockerfile.frontend, порт 3000, depends_on: api

**Переменные окружения:**
- PostgreSQL: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
- Bot: TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, OPENAI_MODEL, DATABASE_URL, SYSTEM_PROMPT_FILE, ROLE_NAME, MAX_CONTEXT_MESSAGES, LOG_LEVEL
- API: DATABASE_URL, LOG_LEVEL
- Frontend:
  - `NEXT_PUBLIC_API_URL=http://localhost:8000` (для браузера клиента)
  - `API_HOST=http://api:8000` (для SSR внутри Docker)

**Network:** llm-network (единая сеть для всех сервисов)

**Миграции БД:** Добавить entrypoint скрипт для API сервиса, который запускает `alembic upgrade head` перед стартом

**⚠️ Безопасность (PostgreSQL):**
- Порт 5432 открыт для dev (доступ с localhost)
- Для production: убрать `ports:` или использовать internal network

### 5. .dockerignore файлы
**Файлы:**
- `.dockerignore` (в корне проекта - для Bot и API)
- `frontend/app/.dockerignore` (для Frontend)

**Корневой .dockerignore (Bot/API):**
```
.git
.gitignore
.env
.env.local
.env.example
README.md
docs/
devops/
frontend/
node_modules
__pycache__
*.pyc
.pytest_cache
.mypy_cache
tests/
*.egg-info
.venv
venv
coverage.json
.ruff_cache
```

**⚠️ ВАЖНО (Безопасность):**
- `.env` исключен из образов (НЕ попадет в Docker image)
- `alembic/` НЕ исключен - нужен для миграций в API контейнере
- Реальные секреты только в `.env` (уже в `.gitignore`)

**frontend/app/.dockerignore (Frontend):**
```
.git
.gitignore
.env
.env.local
.next
.turbo
node_modules
dist
build
README.md
```

### 6. .env.example
**Файл:** `.env.example`

Шаблон с комментариями для всех переменных, необходимых docker-compose:
```bash
# PostgreSQL
POSTGRES_DB=llm_assistant
POSTGRES_USER=llm_user
POSTGRES_PASSWORD=llm_password_dev
POSTGRES_PORT=5432

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_PROXY_URL=https://api.your-proxy.com/v1
OPENAI_MODEL=gpt-4o-mini

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Database URL (для приложений Bot и API)
DATABASE_URL=postgresql+asyncpg://llm_user:llm_password_dev@postgres:5432/llm_assistant

# Bot Configuration
SYSTEM_PROMPT_FILE=prompts/default.txt
ROLE_NAME=AI Assistant
ROLE_DESCRIPTION=Универсальный ИИ-ассистент
MAX_CONTEXT_MESSAGES=10
LOG_LEVEL=INFO

# Frontend (Next.js)
NEXT_PUBLIC_API_URL=http://localhost:8000
API_HOST=http://api:8000
```

### 7. Обновление README.md
Добавить раздел "Docker Compose запуск" с 3 простыми шагами:
1. Скопировать .env: `cp .env.example .env`
2. Заполнить переменные в .env (OPENAI_API_KEY, TELEGRAM_BOT_TOKEN)
3. Запустить: `docker-compose up`

Указать доступные адреса:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- PostgreSQL: localhost:5432

## Технические детали

### Архитектура сервисов
```
┌─────────────────┐
│   PostgreSQL    │ (5432)
│   postgres:17   │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    │           │          │
┌───▼─┐    ┌───▼────┐  ┌──▼──────┐
│ Bot │    │  API   │  │Frontend  │
│     │    │ 8000   │  │  3000    │
└─────┘    └────────┘  └──────────┘
```

### Образы (Alpine минимальные, но полнофункциональные)
- Bot: `python:3.12-alpine` (~50MB)
- API: `python:3.12-alpine` (~50MB)
- Frontend: `node:22-alpine` (~40MB)
- PostgreSQL: `postgres:17-alpine` (~90MB)

### Порты
- Frontend: 3000 (Next.js)
- API: 8000 (FastAPI)
- PostgreSQL: 5432 (база данных)
- Bot: внутренний сервис (нет портов)

### Переменные окружения
Все сервисы читают из `.env` через docker-compose.

### Healthchecks
- PostgreSQL: `pg_isready` (уже в docker-compose.dev.yml)
- Frontend: простой сервис, зависит от API
- API: зависит от PostgreSQL
- Bot: зависит от PostgreSQL

## Проверка работоспособности

После `docker-compose up`:
1. Frontend доступен: http://localhost:3000
2. API доступен: http://localhost:8000
3. PostgreSQL доступен: localhost:5432
4. Bot работает в фоне (логи видны в консоли docker-compose)

## Итоговые файлы

По завершении спринта D0 в проекте появятся:
```
systech-aidd_mcr/
├── Dockerfile.bot                         # NEW
├── Dockerfile.api                         # NEW
├── Dockerfile.frontend                    # NEW
├── entrypoint-api.sh                      # NEW
├── docker-compose.yml                     # NEW
├── .dockerignore                          # NEW (для Bot/API)
├── .env.example                           # NEW
├── frontend/app/.dockerignore             # NEW
├── README.md                              # UPDATED
└── devops/doc/devops-roadmap.md           # UPDATED
```

---

## 🔒 Безопасность (Security Checklist)

### Секреты и credentials
✅ **`.env` в `.gitignore`** - файл не попадет в Git
✅ **`.env` в `.dockerignore`** - файл не попадет в Docker образы
✅ **`.env.example`** - только примеры, БЕЗ реальных секретов
✅ **Переменные через docker-compose** - секреты передаются в runtime, не в build time

### Docker образы
✅ **Нет COPY .env** в Dockerfile - секреты не в образе
✅ **alembic/ включен** - миграции нужны для работы API
✅ **entrypoint-api.sh executable** - chmod +x в Dockerfile

### Сеть и порты
⚠️ **PostgreSQL 5432** - открыт для dev (localhost доступ)
⚠️ **API 8000** - открыт для dev и frontend
⚠️ **Frontend 3000** - открыт для браузера
✅ **Bot internal** - нет внешних портов

### Рекомендации для production (спринт D2-D3)
- 🔐 Использовать secrets manager (Docker secrets, GitHub secrets)
- 🔐 Закрыть PostgreSQL порт (только internal network)
- 🔐 HTTPS для API и Frontend (Nginx reverse proxy)
- 🔐 Ограничить ресурсы контейнеров (CPU, Memory limits)

---

## TODO - Список задач (MVP подход)

### Фаза 1: Dockerfile (Простота, без оптимизаций)
- [ ] **D0.1** Создать `Dockerfile.bot` на python:3.12-alpine (single-stage, ~35 строк)
- [ ] **D0.2** Создать `Dockerfile.api` на python:3.12-alpine с entrypoint для миграций (single-stage, ~40 строк)
- [ ] **D0.3** Создать `Dockerfile.frontend` на node:22-alpine (single-stage, ~25 строк)
- [ ] **D0.4** Создать `entrypoint-api.sh` скрипт для запуска миграций перед стартом API

### Фаза 2: Docker Compose & Config
- [ ] **D0.5** Создать `docker-compose.yml` с 4 сервисами (postgres, bot, api, frontend) с правильными build contexts
- [ ] **D0.6** Создать `.dockerignore` в корне (для Bot/API)
- [ ] **D0.7** Создать `frontend/app/.dockerignore` (для Frontend)
- [ ] **D0.8** Создать `.env.example` с примерами всех переменных (включая NEXT_PUBLIC_API_URL)

### Фаза 3: Документация
- [ ] **D0.9** Обновить `README.md` с разделом "Docker Compose запуск" (3 шага + адреса сервисов)

### Фаза 4: Тестирование & Завершение
- [ ] **D0.10** Локальное тестирование: `docker-compose up`, проверка всех 4 сервисов
- [ ] **D0.11** Проверка миграций БД (должны применяться автоматически)
- [ ] **D0.12** Security audit: проверить что .env не в образах (`docker image inspect`)
- [ ] **D0.13** Актуализировать `devops/doc/devops-roadmap.md` (статус D0 ✅ Completed, ссылка на план)

---

## Критерии готовности (Definition of Done)

### Функциональность
✅ **Все 4 сервиса запускаются:** `docker-compose up` без ошибок
✅ **PostgreSQL готов:** localhost:5432 (первым стартует)
✅ **Миграции применены:** `alembic upgrade head` выполнен автоматически
✅ **API доступен:** http://localhost:8000 (или /docs для Swagger)
✅ **Frontend доступен:** http://localhost:3000 (подключается к API)
✅ **Bot работает:** видны логи в консоли docker-compose

### Документация
✅ **README обновлен:** секция "Docker Compose запуск" с 3 шагами
✅ **.env.example создан:** все переменные задокументированы
✅ **Roadmap обновлен:** статус D0 = ✅ Completed, ссылка на план добавлена

### Безопасность
✅ **`.env` в `.gitignore`:** секреты не в Git
✅ **`.env` в `.dockerignore`:** секреты не в Docker образах
✅ **Security audit passed:** `docker image inspect` - нет .env файлов в образах
