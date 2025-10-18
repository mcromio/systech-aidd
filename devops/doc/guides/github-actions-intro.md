# GitHub Actions - Краткое введение

> Дата создания: 18.10.2025
> Спринт: D1 - Build & Publish

## Что такое GitHub Actions?

**GitHub Actions** — это платформа CI/CD (Continuous Integration / Continuous Deployment), встроенная в GitHub. Она позволяет автоматизировать задачи разработки: сборку, тестирование, деплой и многое другое.

### Зачем нужны GitHub Actions?

- ✅ Автоматическая сборка Docker образов при каждом push
- ✅ Публикация образов в GitHub Container Registry (ghcr.io)
- ✅ Запуск тестов и проверок кода
- ✅ Автоматический деплой на сервер
- ✅ Уведомления о статусе сборки

---

## Основные концепции

### 1. Workflow (Рабочий процесс)

YAML файл в директории `.github/workflows/`, описывающий автоматизированный процесс.

**Пример:** `.github/workflows/build.yml`

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
```

### 2. Jobs (Задачи)

Независимые единицы работы в workflow. Могут выполняться параллельно или последовательно.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    runs-on: ubuntu-latest
    needs: build  # Выполнится после build
    steps: [...]
```

### 3. Steps (Шаги)

Отдельные команды или действия внутри job.

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4

  - name: Run tests
    run: pytest tests/
```

### 4. Actions (Действия)

Переиспользуемые модули для типовых задач.

**Популярные actions:**
- `actions/checkout@v4` - клонирование репозитория
- `docker/login-action@v3` - авторизация в Docker registry
- `docker/build-push-action@v5` - сборка и публикация образов

---

## Triggers (События запуска)

### Push

Запуск при push в определенные ветки:

```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - 'Dockerfile.*'
```

### Pull Request

Запуск при создании/обновлении PR:

```yaml
on:
  pull_request:
    branches: [main]
```

### Workflow Dispatch

Ручной запуск через GitHub UI:

```yaml
on:
  workflow_dispatch:  # Кнопка "Run workflow" в UI
```

### Комбинирование

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

---

## GitHub Container Registry (ghcr.io)

**GHCR** — реестр Docker образов, встроенный в GitHub.

### Преимущества:

- ✅ Интеграция с GitHub - единый аккаунт
- ✅ Бесплатно для публичных репозиториев
- ✅ Автоматическая авторизация через `GITHUB_TOKEN`
- ✅ Контроль доступа через GitHub permissions
- ✅ Версионирование образов через теги

### Формат образов:

```
ghcr.io/OWNER/REPO-NAME:TAG
```

**Пример:**
```
ghcr.io/mcromio/systech-aidd-bot:latest
ghcr.io/mcromio/systech-aidd-bot:sha-abc1234
```

### Public vs Private packages

| Тип | Доступ | Pull без auth | Использование |
|-----|--------|---------------|---------------|
| **Public** | Всем | ✅ Да | MVP, открытые проекты |
| **Private** | Только с токеном | ❌ Нет | Продакшен, закрытый код |

**Для MVP используем Public packages** - проще и быстрее.

---

## Matrix Strategy (Параллельная сборка)

**Matrix** позволяет запускать один job с разными параметрами параллельно.

### Пример: сборка 3 образов одновременно

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
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

    steps:
      - name: Build ${{ matrix.service }}
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.context }}
          file: ${{ matrix.context }}/${{ matrix.dockerfile }}
          push: true
          tags: ghcr.io/owner/repo-${{ matrix.service }}:latest
```

**Преимущества:**
- ⚡ Параллельное выполнение - экономия времени
- 🔄 DRY принцип - один код для всех сервисов
- 🎯 Легко масштабировать - добавить новый сервис просто

---

## Практический пример: Полный workflow

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main, devops]
    paths:
      - 'Dockerfile.*'
      - 'src/**'
      - 'frontend/**'
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

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

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push ${{ matrix.service }}
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.context }}
          file: ${{ matrix.context }}/${{ matrix.dockerfile }}
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/systech-aidd-${{ matrix.service }}:latest
            ghcr.io/${{ github.repository_owner }}/systech-aidd-${{ matrix.service }}:${{ github.sha }}
```

---

## Просмотр статуса workflow

### В GitHub UI:

1. Перейти в репозиторий
2. Вкладка **Actions**
3. Выбрать workflow
4. Посмотреть логи каждого job

### Badge в README:

```markdown
[![Build Status](https://github.com/mcromio/systech-aidd/actions/workflows/build.yml/badge.svg)](https://github.com/mcromio/systech-aidd/actions/workflows/build.yml)
```

---

## Полезные ссылки

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

## Следующие шаги

1. ✅ Прочитать эту инструкцию
2. ➡️ Настроить GitHub Container Registry: [github-registry-setup.md](github-registry-setup.md)
3. ➡️ Создать workflow: `.github/workflows/build.yml`
4. ➡️ Протестировать workflow: [testing-workflow.md](testing-workflow.md)

