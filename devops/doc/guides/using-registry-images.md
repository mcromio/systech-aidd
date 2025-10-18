# Использование образов из GitHub Container Registry

> Дата создания: 18.10.2025
> Спринт: D1 - Build & Publish

## Обзор

Эта инструкция описывает как использовать опубликованные Docker образы из GitHub Container Registry (ghcr.io) для запуска приложения.

---

## Доступные образы

После публикации доступны следующие образы:

| Сервис | Образ | Описание |
|--------|-------|----------|
| **Bot** | `ghcr.io/mcromio/systech-aidd-bot:latest` | Telegram бот |
| **API** | `ghcr.io/mcromio/systech-aidd-api:latest` | FastAPI backend |
| **Frontend** | `ghcr.io/mcromio/systech-aidd-frontend:latest` | Next.js веб-интерфейс |

---

## Способ 1: Использование через docker-compose.prod.yml (Рекомендуется)

### Шаг 1: Подготовка окружения

```bash
# Склонировать репозиторий (если еще не склонирован)
git clone https://github.com/mcromio/systech-aidd.git
cd systech-aidd

# Создать .env файл из примера
cp .env.example .env

# Отредактировать .env - заполнить обязательные переменные
notepad .env  # Windows
nano .env     # Linux/macOS
```

**Обязательные переменные в .env:**
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Шаг 2: Pull образов

```bash
# Через Makefile
make compose-pull

# Или напрямую
docker-compose -f docker-compose.prod.yml pull
```

**Что происходит:**
- Скачиваются последние версии образов из ghcr.io
- Образы сохраняются локально
- Не требуется авторизация (если packages публичные)

### Шаг 3: Запуск сервисов

```bash
# Через Makefile (автоматически pull + up)
make compose-prod

# Или вручную
docker-compose -f docker-compose.prod.yml up -d
```

### Шаг 4: Проверка работы

```bash
# Статус сервисов
docker-compose -f docker-compose.prod.yml ps

# Логи
docker-compose -f docker-compose.prod.yml logs -f

# API health check
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

### Шаг 5: Остановка

```bash
# Через Makefile
make compose-down

# Или вручную
docker-compose -f docker-compose.prod.yml down
```

---

## Способ 2: Ручной pull и запуск отдельных образов

### Pull конкретного образа:

```bash
# Bot
docker pull ghcr.io/mcromio/systech-aidd-bot:latest

# API
docker pull ghcr.io/mcromio/systech-aidd-api:latest

# Frontend
docker pull ghcr.io/mcromio/systech-aidd-frontend:latest
```

### Запуск отдельного контейнера:

```bash
# Пример: запуск API
docker run -d \
  --name systech-aidd-api \
  --env-file .env \
  -p 8000:8000 \
  ghcr.io/mcromio/systech-aidd-api:latest

# Пример: запуск Frontend
docker run -d \
  --name systech-aidd-frontend \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -p 3000:3000 \
  ghcr.io/mcromio/systech-aidd-frontend:latest
```

---

## Работа с версиями (Tags)

### Доступные теги:

| Тег | Описание | Пример |
|-----|----------|--------|
| `latest` | Последняя версия из main/devops ветки | `ghcr.io/mcromio/systech-aidd-bot:latest` |
| `sha-XXXXXXX` | Конкретный commit | `ghcr.io/mcromio/systech-aidd-bot:sha-abc1234` |

### Использование конкретной версии:

```bash
# Pull конкретного коммита
docker pull ghcr.io/mcromio/systech-aidd-bot:sha-abc1234

# Запуск конкретной версии
docker run -d \
  --env-file .env \
  ghcr.io/mcromio/systech-aidd-bot:sha-abc1234
```

### В docker-compose.prod.yml:

```yaml
services:
  bot:
    # Вместо latest использовать конкретную версию
    image: ghcr.io/mcromio/systech-aidd-bot:sha-abc1234
```

---

## Обновление образов

### Автоматическое обновление до latest:

```bash
# Pull новых версий
make compose-pull

# Перезапуск с новыми образами
make compose-prod
```

### Ручное обновление:

```bash
# Остановить сервисы
docker-compose -f docker-compose.prod.yml down

# Pull обновленных образов
docker-compose -f docker-compose.prod.yml pull

# Запустить с новыми образами
docker-compose -f docker-compose.prod.yml up -d
```

### Откат на предыдущую версию:

```bash
# Найти нужный commit SHA в GitHub
# Обновить docker-compose.prod.yml с конкретным тегом
# Перезапустить сервисы

docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## Использование на удаленном сервере

### Подготовка сервера:

```bash
# SSH на сервер
ssh user@your-server.com

# Установить Docker (если не установлен)
curl -fsSL https://get.docker.com | sh

# Установить Docker Compose
sudo apt-get install docker-compose-plugin
```

### Развертывание:

```bash
# Склонировать репозиторий
git clone https://github.com/mcromio/systech-aidd.git
cd systech-aidd

# Создать .env с продакшен переменными
nano .env

# Pull и запуск
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Проверка
docker-compose -f docker-compose.prod.yml ps
```

---

## Переменные окружения

### Обязательные для Bot:

```bash
TELEGRAM_BOT_TOKEN=xxx           # Токен бота из @BotFather
OPENAI_API_KEY=xxx              # OpenAI API ключ
OPENAI_MODEL=gpt-4o-mini        # Модель LLM
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db
```

### Обязательные для API:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db
LOG_LEVEL=INFO
```

### Обязательные для Frontend:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000   # Для браузера
API_HOST=http://api:8000                    # Для SSR в Docker
```

### База данных (PostgreSQL):

```bash
POSTGRES_DB=llm_assistant
POSTGRES_USER=llm_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432
```

---

## Авторизация для Private packages

Если образы сделаны приватными:

### Создание токена:

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Scopes: `read:packages`
4. Скопировать токен

### Login в Docker:

```bash
# Авторизация
echo YOUR_TOKEN | docker login ghcr.io -u mcromio --password-stdin

# Pull образов
docker pull ghcr.io/mcromio/systech-aidd-bot:latest

# Logout (опционально)
docker logout ghcr.io
```

---

## Мониторинг и логи

### Просмотр логов:

```bash
# Все сервисы
docker-compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f bot
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f frontend

# Последние N строк
docker-compose -f docker-compose.prod.yml logs --tail=100 api
```

### Статус контейнеров:

```bash
# Через docker-compose
docker-compose -f docker-compose.prod.yml ps

# Напрямую через docker
docker ps | grep systech-aidd

# Детальная информация
docker inspect llm-assistant-api
```

### Health checks:

```bash
# API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# PostgreSQL (внутри контейнера)
docker exec llm-assistant-db pg_isready -U llm_user
```

---

## Troubleshooting

### Ошибка: "unauthorized: unauthenticated"

**Проблема:** Образы private, нужна авторизация

**Решение:**
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u mcromio --password-stdin
```

---

### Ошибка: "manifest unknown"

**Проблема:** Образ не существует или неправильный тег

**Решение:**
1. Проверить что workflow выполнился успешно
2. Проверить наличие packages на GitHub
3. Проверить правильность имени образа

---

### Сервис не запускается

**Проблема:** Отсутствуют переменные окружения

**Решение:**
```bash
# Проверить .env файл
cat .env

# Проверить логи
docker-compose -f docker-compose.prod.yml logs bot

# Проверить переменные в контейнере
docker exec llm-assistant-bot env
```

---

### Старая версия образа

**Проблема:** Docker использует закэшированный образ

**Решение:**
```bash
# Удалить старые образы
docker rmi ghcr.io/mcromio/systech-aidd-bot:latest

# Pull свежей версии
docker-compose -f docker-compose.prod.yml pull

# Перезапуск
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

---

## Полезные команды

```bash
# Информация об образе
docker image inspect ghcr.io/mcromio/systech-aidd-bot:latest

# Размер образа
docker image ls ghcr.io/mcromio/systech-aidd-bot:latest

# История слоев
docker history ghcr.io/mcromio/systech-aidd-bot:latest

# Удалить образ локально
docker rmi ghcr.io/mcromio/systech-aidd-bot:latest

# Очистка неиспользуемых образов
docker image prune -a

# Экспорт образа в файл
docker save ghcr.io/mcromio/systech-aidd-bot:latest -o bot.tar

# Импорт образа из файла
docker load -i bot.tar
```

---

## Best Practices

### ✅ Рекомендуется:

- Использовать `docker-compose.prod.yml` для запуска всех сервисов
- Хранить `.env` файл в безопасном месте
- Регулярно обновлять образы (`compose-pull`)
- Использовать конкретные теги (sha-XXX) в продакшене
- Проверять логи после запуска

### ❌ Не рекомендуется:

- Хранить `.env` в git репозитории
- Использовать `latest` тег в продакшене без версионирования
- Запускать без healthchecks
- Игнорировать ошибки в логах

---

## Дальнейшие шаги

1. ✅ Образы успешно используются локально
2. ➡️ Автоматизация деплоя: Спринт D2 - Развертывание на сервер
3. ➡️ CI/CD pipeline: Спринт D3 - Auto Deploy

---

## Полезные ссылки

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Packages](https://github.com/users/mcromio/packages?repo_name=systech-aidd)
- [Docker CLI Reference](https://docs.docker.com/engine/reference/commandline/cli/)

