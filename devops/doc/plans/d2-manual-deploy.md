# План Спринта D2: Развертывание на сервер

## Описание

Спринт D2 направлен на создание инструкции и подготовку файлов для ручного развертывания приложения на production сервере с использованием готовых Docker образов из GitHub Container Registry.

## Цели

1. Создать детальную пошаговую инструкцию по развертыванию
2. Подготовить конфигурационные файлы для production окружения
3. Обеспечить возможность быстрого и безошибочного деплоя
4. Заложить основу для автоматизации в следующем спринте (D3)

## Параметры Production окружения

### Сервер
- **Адрес:** 89.223.67.136 (в документации: `<server_address>`)
- **Пользователь:** systech
- **SSH доступ:** через ключ
- **Рабочая директория:** `/opt/systech/rdolgovitskiy`

### Порты
- **API:** 8003 (внешний и внутренний)
- **Frontend:** 3003 (внешний) → 3000 (внутренний)
- **PostgreSQL:** только внутренний доступ (без expose)

### Docker образы
- Bot: `ghcr.io/mcromio/systech-aidd-bot:latest`
- API: `ghcr.io/mcromio/systech-aidd-api:latest`
- Frontend: `ghcr.io/mcromio/systech-aidd-frontend:latest`

## Список задач

### 1. Создание шаблона переменных окружения ✅

**Файл:** `env.production.example`

**Содержание:**
- Все необходимые переменные с подробными комментариями
- Описание каждой переменной и где получить значения
- Примеры значений для production
- Checklist для проверки перед запуском

**Обязательные переменные:**
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`, `OPENAI_PROXY_URL`, `OPENAI_MODEL`
- `API_HOST`, `API_PORT`
- `NEXT_PUBLIC_API_URL`, `API_HOST`
- `LOG_LEVEL`, `DATABASE_URL`

### 2. Модификация docker-compose.prod.yml ✅

**Изменения:**
- ✅ Изменены порты API: `8003:8003` (было `8000:8000`)
- ✅ Изменены порты Frontend: `3003:3000` (было `3000:3000`)
- ✅ Убран expose PostgreSQL (только внутренний доступ)
- ✅ Обновлены переменные окружения для правильных портов
- ✅ Добавлены volumes для промптов: `./prompts:/app/prompts:ro`
- ✅ Обновлен healthcheck для API на порт 8003

### 3. Создание инструкции по развертыванию ✅

**Файл:** `devops/doc/guides/manual-deploy.md`

**Структура:**
- **Обзор:** Описание процесса, параметры, время
- **Предварительные требования:** Что нужно локально и на сервере
- **Шаг 1: Подготовка локально**
  - Клонирование репозитория
  - Создание .env из шаблона
  - Проверка SSH ключа
- **Шаг 2: Подключение к серверу**
  - SSH подключение
  - Проверка Docker и Docker Compose
- **Шаг 3: Развертывание**
  - Создание рабочей директории
  - Копирование файлов через scp
  - Pull образов
  - Запуск сервисов
- **Шаг 4: Проверка работоспособности**
  - Статус контейнеров
  - Проверка логов
  - Healthcheck API
  - Тестирование доступности снаружи
  - Тестирование Telegram бота
- **Шаг 5: Управление сервисами**
  - Основные команды
  - Статус и мониторинг
- **Troubleshooting:** Типичные проблемы и решения
- **Безопасность:** Рекомендации по безопасности
- **Следующие шаги:** Что делать после деплоя

### 4. Создание плана спринта ✅

**Файл:** `devops/doc/plans/d2-manual-deploy.md` (этот файл)

### 5. Обновление roadmap ⏳

**Файл:** `devops/doc/devops-roadmap.md`

**Изменения:**
- Статус D2: `⏳ Pending` → `✅ Completed`
- Добавить ссылку на план: `[План D2](plans/d2-manual-deploy.md)`

## Файлы созданные/измененные

### Созданные файлы:
1. `env.production.example` - Шаблон переменных окружения
2. `devops/doc/guides/manual-deploy.md` - Инструкция по развертыванию
3. `devops/doc/plans/d2-manual-deploy.md` - План спринта

### Измененные файлы:
1. `docker-compose.prod.yml` - Порты и конфигурация для production
2. `devops/doc/devops-roadmap.md` - Статус спринта D2

## Процесс развертывания (краткий)

```bash
# 1. Локально: подготовить .env
cp env.production.example .env
nano .env  # заполнить секреты

# 2. Подключиться к серверу
ssh -i <key> systech@89.223.67.136

# 3. Создать директорию
sudo mkdir -p /opt/systech/rdolgovitskiy
cd /opt/systech/rdolgovitskiy

# 4. Скопировать файлы (с локального компьютера)
scp -i <key> docker-compose.prod.yml systech@89.223.67.136:/opt/systech/rdolgovitskiy/
scp -i <key> .env systech@89.223.67.136:/opt/systech/rdolgovitskiy/
scp -i <key> -r prompts systech@89.223.67.136:/opt/systech/rdolgovitskiy/
scp -i <key> -r scripts systech@89.223.67.136:/opt/systech/rdolgovitskiy/

# 5. На сервере: запустить
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# 6. Проверить
docker compose -f docker-compose.prod.yml ps
curl http://localhost:8003/health
```

## Критерии готовности

- [x] env.production.example содержит все переменные с комментариями
- [x] docker-compose.prod.yml настроен для портов 8003/3003
- [x] PostgreSQL не expose наружу
- [x] Volumes для промптов добавлены
- [x] manual-deploy.md содержит детальную инструкцию
- [x] Все команды готовы для copy-paste
- [x] Инструкция содержит troubleshooting секцию
- [x] План спринта создан
- [ ] devops-roadmap.md обновлен

## Чеклист перед ручным развертыванием

### Подготовка:
- [ ] Клонирован репозиторий
- [ ] Создан .env файл из env.production.example
- [ ] Заполнены все обязательные переменные в .env:
  - [ ] POSTGRES_PASSWORD (сильный пароль)
  - [ ] TELEGRAM_BOT_TOKEN
  - [ ] OPENAI_API_KEY
  - [ ] NEXT_PUBLIC_API_URL (с IP сервера)
- [ ] Есть SSH ключ для доступа к серверу
- [ ] SSH ключ добавлен в ssh-agent или указан путь

### На сервере:
- [ ] Подключение к серверу работает
- [ ] Docker установлен и работает
- [ ] Docker Compose версии 2.0+
- [ ] Создана рабочая директория /opt/systech/rdolgovitskiy
- [ ] Файлы скопированы на сервер
- [ ] Права на .env установлены (chmod 600)

### Развертывание:
- [ ] Образы успешно загружены (docker compose pull)
- [ ] Сервисы запущены (docker compose up -d)
- [ ] Все контейнеры в статусе Up/Healthy
- [ ] API healthcheck работает (curl localhost:8003/health)
- [ ] API доступен снаружи (http://89.223.67.136:8003/docs)
- [ ] Frontend доступен снаружи (http://89.223.67.136:3003)
- [ ] Telegram бот отвечает на сообщения

### Безопасность:
- [ ] .env файл не закоммичен в git
- [ ] Права на .env: 600 (только владелец)
- [ ] Использован сильный пароль для PostgreSQL
- [ ] Firewall настроен (порты 8003, 3003)

## Следующий спринт: D3 - Auto Deploy

После успешного ручного развертывания в D2, следующий спринт D3 будет посвящен автоматизации:

- Создание GitHub Actions workflow для автоматического деплоя
- Настройка SSH ключей в GitHub Secrets
- Автоматический деплой при push в main ветку
- Уведомления о статусе деплоя
- Rollback механизм

## Время выполнения

- **Планирование:** 30 минут
- **Создание файлов:** 1 час
- **Тестирование инструкции:** 20 минут (ручной деплой)
- **Документация:** 30 минут
- **Итого:** ~2.5 часа

## Заметки

1. Инструкция написана для пользователя без глубоких знаний DevOps
2. Все команды готовы к копированию
3. Добавлен раздел troubleshooting с типичными проблемами
4. Включены примеры с реальным IP сервера
5. Добавлен checklist для проверки перед деплоем
6. Документированы все переменные окружения

## Связанные документы

- [DevOps Roadmap](../devops-roadmap.md)
- [Инструкция по развертыванию](../guides/manual-deploy.md)
- [План D0: Basic Docker Setup](d0-basic-docker-setup.md)
- [План D1: Build & Publish](d1-build-publish.md)
- Следующий: План D3: Auto Deploy (будет создан)

