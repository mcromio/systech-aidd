# Спринт D1: Build & Publish - План реализации

> **Дата создания:** 18.10.2025
> **Статус:** ✅ Completed
> **Фокус:** Автоматизация сборки и публикации Docker образов в GitHub Container Registry

## Цель

Автоматическая сборка Docker образов через GitHub Actions и публикация в GitHub Container Registry (ghcr.io) с публичным доступом.

## Контекст

После успешного завершения D0 у нас есть:
- ✅ Dockerfile.bot, Dockerfile.api, Dockerfile.frontend
- ✅ docker-compose.yml для локальной сборки
- ✅ Все 4 сервиса работают локально

Теперь нужно автоматизировать сборку для использования в D2 (ручной deploy) и D3 (auto deploy).

---

## Фаза 1: Документация GitHub Actions

### Файл: `devops/doc/guides/github-actions-intro.md`

Краткое введение в GitHub Actions:

**Содержание:**
- Что такое GitHub Actions и зачем нужны
- Основные концепции: workflows, jobs, steps, actions
- Triggers (события): push, pull_request, workflow_dispatch
- GitHub Container Registry (ghcr.io) - что это и зачем
- Public vs Private packages
- Matrix strategy для параллельной сборки

**Примеры:**
- Простой workflow
- Trigger на push в main
- Matrix для нескольких образов
- Публикация в ghcr.io

---

## Фаза 2: GitHub Actions Workflow

### Файл: `.github/workflows/build.yml`

**Trigger:**
```yaml
on:
  push:
    branches: [main, devops]
    paths:
      - 'Dockerfile.*'
      - 'src/**'
      - 'frontend/**'
      - 'pyproject.toml'
      - 'package.json'
      - 'pnpm-lock.yaml'
      - 'alembic/**'
      - '.github/workflows/build.yml'
  workflow_dispatch:
```

**Jobs:**
1. **build-and-push** - параллельная сборка и публикация 3 образов

**Matrix Strategy:**
```yaml
strategy:
  matrix:
    include:
      - service: bot
        dockerfile: Dockerfile.bot
        context: .
      - service: api
        dockerfile: Dockerfile.api
        context: .
      - service: frontend
        dockerfile: Dockerfile
        context: ./frontend/app
```

**Steps:**
1. Checkout code
2. Docker meta (теги: latest, sha-short)
3. Login to ghcr.io (через GITHUB_TOKEN)
4. Setup Docker Buildx (для кэширования)
5. Build and push с cache
6. **Security check: verify no secrets in image**
7. Image summary

**Тегирование:**
- `ghcr.io/mcromio/systech-aidd-bot:latest`
- `ghcr.io/mcromio/systech-aidd-bot:sha-abc1234`

**Кэширование:**
```yaml
cache-from: type=registry,ref=ghcr.io/mcromio/systech-aidd-bot:buildcache
cache-to: type=registry,ref=ghcr.io/mcromio/systech-aidd-bot:buildcache,mode=max
```

**Security Check:**
- Проверка отсутствия .env файлов в образах
- Проверка ENV переменных на наличие секретов
- Автоматический fail если найдены проблемы

---

## Фаза 3: Настройка GitHub Container Registry

### Файл: `devops/doc/guides/github-registry-setup.md`

**Инструкция по настройке:**

1. **Workflow Permissions:**
   - Settings → Actions → General → Workflow permissions
   - Выбрать: "Read and write permissions"

2. **GITHUB_TOKEN:**
   - Используется автоматически (не нужен PAT)
   - Доступен в `secrets.GITHUB_TOKEN`

3. **Сделать packages публичными:**
   - После первой публикации: ghcr.io → Package settings
   - Change visibility → Public
   - Повторить для bot, api, frontend

4. **Безопасность:**
   - Проверка .dockerignore
   - Никаких hardcoded секретов
   - Public packages = код виден всем

---

## Фаза 4: Интеграция с docker-compose

### Создано: `docker-compose.prod.yml`

Версия для использования образов из registry:

```yaml
services:
  bot:
    image: ghcr.io/mcromio/systech-aidd-bot:latest
    env_file: .env

  api:
    image: ghcr.io/mcromio/systech-aidd-api:latest
    env_file: .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]

  frontend:
    image: ghcr.io/mcromio/systech-aidd-frontend:latest
```

**Ключевые моменты:**
- Все сервисы используют image вместо build
- env_file: .env обязателен для bot и api
- healthcheck для api (для depends_on frontend)

### Обновлено: `Makefile`

Добавлены команды для работы с registry:

```makefile
compose-build      # Локальная сборка
compose-prod       # Запуск из registry (с автоматическим pull)
compose-pull       # Pull образов из ghcr.io
compose-up         # Запуск без rebuild
compose-down       # Остановить сервисы
compose-logs       # Просмотр логов
compose-ps         # Статус сервисов
```

---

## Фаза 5: Тестирование

### Файл: `devops/doc/guides/testing-workflow.md`

**Методы тестирования:**

1. **Ручной запуск через GitHub UI (рекомендуется):**
   - Actions → Run workflow → devops branch

2. **Автоматический trigger при push:**
   - Изменение в src/, frontend/, Dockerfile.*

3. **Локальное тестирование с Act (опционально):**
   - `act -l` - список workflows
   - `act push` - эмуляция push event

**Проверка образов:**
```bash
docker pull ghcr.io/mcromio/systech-aidd-bot:latest
docker image inspect ghcr.io/mcromio/systech-aidd-bot:latest
docker run --rm ghcr.io/mcromio/systech-aidd-bot:latest python --version
```

**Запуск через docker-compose.prod.yml:**
```bash
make compose-prod
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

---

## Фаза 6: Документация

### Обновлено: `README.md`

**Добавлено:**

1. **CI/CD Status секция:**
```markdown
[![Build and Push](https://github.com/mcromio/systech-aidd/actions/workflows/build.yml/badge.svg)](...)

Доступные образы:
- ghcr.io/mcromio/systech-aidd-bot:latest
- ghcr.io/mcromio/systech-aidd-api:latest
- ghcr.io/mcromio/systech-aidd-frontend:latest
```

2. **Использование готовых образов:**
```bash
make compose-prod
# или
docker-compose -f docker-compose.prod.yml up -d
```

3. **Docker Compose команды:**
- compose-build, compose-prod, compose-pull, etc.

### Создано: `devops/doc/guides/using-registry-images.md`

Детальная инструкция:
- Pull и запуск образов
- Работа с версиями (tags)
- Обновление образов
- Использование на удаленном сервере
- Переменные окружения
- Troubleshooting

---

## Структура файлов

После D1 в проекте:

```
.github/
└── workflows/
    └── build.yml                       ✅ NEW

devops/doc/
├── guides/
│   ├── github-actions-intro.md        ✅ NEW
│   ├── github-registry-setup.md       ✅ NEW
│   ├── testing-workflow.md            ✅ NEW
│   └── using-registry-images.md       ✅ NEW
├── plans/
│   ├── d0-basic-docker-setup.md       (D0)
│   └── d1-build-publish.md            ✅ NEW (этот файл)
└── devops-roadmap.md                   ✅ UPDATED

docker-compose.prod.yml                 ✅ NEW
Makefile                                ✅ UPDATED
README.md                               ✅ UPDATED

frontend/app/
└── Dockerfile                          ✅ MOVED (было Dockerfile.frontend)
```

---

## Технические детали

### GitHub Actions

- **Runner:** ubuntu-latest
- **Matrix strategy:** параллельная сборка 3 образов
- **Docker Buildx:** для кэширования layers
- **GITHUB_TOKEN:** автоматическая авторизация

### Тегирование

- `latest` - последний commit в main/devops
- `sha-abc1234` - короткий SHA коммита (7 символов)
- В будущем: `v1.0.0` - semantic versioning (D4+)

### Кэширование

- Registry cache для ускорения сборок
- Кэш сохраняется между запусками
- Уменьшение времени: ~5 мин → ~1 мин

### Security

- .dockerignore исключает .env файлы
- Автоматическая проверка в workflow
- Public packages = код доступен всем

---

## Проверка готовности (Definition of Done)

### Функциональность

- ✅ GitHub Actions workflow создан и работает
- ✅ Образы собираются автоматически при push
- ✅ Образы публикуются в ghcr.io
- ✅ Образы публичные (доступны без auth)
- ✅ Security check проходит для всех образов
- ✅ docker-compose.prod.yml работает с образами из registry

### Документация

- ✅ README обновлен (badges + инструкции)
- ✅ Созданы 4 guide файла
- ✅ Инструкция по настройке ghcr.io
- ✅ Roadmap обновлен (D1 Completed)

### Тестирование

- ✅ Workflow запущен успешно
- ✅ Все 3 образа опубликованы
- ✅ Образы можно pull без авторизации
- ✅ Сервисы запускаются из registry образов
- ✅ API и Frontend доступны

---

## Изменения относительно первоначального плана

### ✅ Добавлено:

1. **Security check step в workflow:**
   - Автоматическая проверка .env файлов
   - Проверка ENV переменных на секреты
   - Fail workflow если найдены проблемы

2. **Перемещение Dockerfile.frontend:**
   - Из корня в `frontend/app/Dockerfile`
   - Упрощение build context

3. **Расширенные trigger paths:**
   - Добавлены: pyproject.toml, package.json, pnpm-lock.yaml, alembic/

4. **Healthcheck для API в docker-compose.prod.yml:**
   - Необходим для depends_on в frontend

5. **env_file: .env в docker-compose.prod.yml:**
   - Для bot и api сервисов

---

## MVP Ограничения (сделаем позже)

Не включено в D1:
- ❌ Linting (ruff, eslint) - D4
- ❌ Tests (pytest, jest) - D4
- ❌ Security scanning (Trivy) - D4
- ❌ Multi-platform builds (amd64, arm64) - D5
- ❌ Image optimization - D5
- ❌ Semantic versioning - D4
- ❌ Release workflow - D4

**Фокус D1:** Работающая автоматическая сборка и публикация для D2/D3!

---

## Примечания

### Почему ghcr.io?

- Интеграция с GitHub
- Бесплатно для публичных репозиториев
- Автоматическая авторизация через GITHUB_TOKEN
- Готовность к private packages

### Почему public packages?

- Простота использования (no auth required)
- MVP подход
- Готовность к D2 (deploy на сервер)
- Позже можно сделать private (D4+)

### Security

⚠️ **ВАЖНО:** Public packages = код виден всем!
- Никаких hardcoded секретов в коде
- .env файлы в .dockerignore
- Автоматическая проверка в workflow

---

## Готовность к следующим спринтам

### D2: Развертывание на сервер
✅ Образы в ghcr.io доступны публично
✅ docker-compose.prod.yml готов к использованию
✅ Документация по использованию образов

### D3: Auto Deploy
✅ GitHub Actions настроены
✅ Workflow для сборки работает
✅ Готовы к добавлению deploy workflow

---

## Полезные команды

```bash
# Локальная работа
make compose-build       # Локальная сборка
make compose-prod        # Запуск из registry

# GitHub Actions
gh workflow run build.yml --ref devops
gh run list --workflow=build.yml
gh run view --log

# Docker
docker pull ghcr.io/mcromio/systech-aidd-bot:latest
docker images | grep systech-aidd
docker-compose -f docker-compose.prod.yml ps
```

---

## Дата завершения: 18.10.2025

**Статус:** ✅ **SPRINT D1 COMPLETED!**

Все задачи выполнены, образы опубликованы, документация создана.

**Готовы к D2: Развертывание на сервер!**

