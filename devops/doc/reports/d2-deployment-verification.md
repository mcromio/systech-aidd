# Отчет о развертывании Спринта D2

## Дата и время
- **Начало:** 18 октября 2025, 14:30 UTC
- **Завершение:** 18 октября 2025, 16:11 UTC
- **Длительность:** ~1 час 41 минута

## Цель
Ручное развертывание приложения на production сервере с использованием Docker образов из GitHub Container Registry.

## Параметры окружения

### Сервер
- **Адрес:** 89.223.67.136
- **Пользователь:** systech
- **Рабочая директория:** /opt/systech/rdolgovitskiy
- **SSH доступ:** Через приватный ключ

### Порты
- **API:** 8003 (внешний) → 8000 (внутренний Docker)
- **Frontend:** 3003 (внешний) → 3000 (внутренний Docker)
- **PostgreSQL:** Только внутренний доступ (без expose)

### Docker образы
- Bot: `ghcr.io/mcromio/systech-aidd-bot:latest`
- API: `ghcr.io/mcromio/systech-aidd-api:latest`
- Frontend: `ghcr.io/mcromio/systech-aidd-frontend:latest`
- PostgreSQL: `postgres:17-alpine`

## Процесс развертывания

### Шаг 1: Подготовка файлов ✅
- Создан `env.production.example` с шаблоном переменных
- Модифицирован `docker-compose.prod.yml` для production портов
- Создана инструкция `devops/doc/guides/manual-deploy.md`

### Шаг 2: Копирование файлов на сервер ✅
```bash
scp -i C:\Users\Mcromo\systech_admin_key.txt docker-compose.prod.yml systech@89.223.67.136:/opt/systech/rdolgovitskiy/
scp -i C:\Users\Mcromo\systech_admin_key.txt env.production.example systech@89.223.67.136:/opt/systech/rdolgovitskiy/.env
scp -i C:\Users\Mcromo\systech_admin_key.txt -r prompts systech@89.223.67.136:/opt/systech/rdolgovitskiy/
scp -i C:\Users\Mcromo\systech_admin_key.txt -r scripts systech@89.223.67.136:/opt/systech/rdolgovitskiy/
```

### Шаг 3: Загрузка образов ✅
```bash
docker compose -f docker-compose.prod.yml pull
```

Все образы успешно загружены:
- postgres:17-alpine
- ghcr.io/mcromio/systech-aidd-bot:latest
- ghcr.io/mcromio/systech-aidd-api:latest
- ghcr.io/mcromio/systech-aidd-frontend:latest

### Шаг 4: Запуск сервисов ✅
```bash
docker compose -f docker-compose.prod.yml up -d
```

## Проблемы и решения

### Проблема 1: Отсутствие `src/api_main.py` в образе
**Причина:** Файлы `src/api/` и `src/api_main.py` не были добавлены в Git репозиторий, поэтому GitHub Actions не включил их в Docker образ.

**Решение:**
1. Добавлены файлы в Git:
   ```bash
   git add src/api/ src/api_main.py tests/test_api_stats.py tests/test_mock_stat_collector.py
   git commit -m "feat(api): add API service with FastAPI (api_main.py, api/ directory)"
   git push origin devops
   ```
2. GitHub Actions автоматически пересобрал образы
3. Повторно загружены обновленные образы на сервер

**Статус:** ✅ Решено

### Проблема 2: Неправильный маппинг портов для API
**Причина:** В `Dockerfile.api` API слушает порт 8000 (`CMD ["uvicorn", "src.api_main:app", "--host", "0.0.0.0", "--port", "8000"]`), но в `docker-compose.prod.yml` был указан маппинг `8003:8003` и healthcheck проверял `localhost:8003`.

**Решение:**
Исправлен `docker-compose.prod.yml`:
```yaml
ports:
  - "8003:8000"  # Вместо "8003:8003"

healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]  # Вместо localhost:8003
```

**Статус:** ✅ Решено

## Результаты проверки

### Статус контейнеров
```
NAME                     IMAGE                                          STATUS
llm-assistant-api        ghcr.io/mcromio/systech-aidd-api:latest        Up 32 seconds (healthy)
llm-assistant-bot        ghcr.io/mcromio/systech-aidd-bot:latest        Up 5 seconds (healthy)
llm-assistant-db         postgres:17-alpine                             Up 37 seconds (healthy)
llm-assistant-frontend   ghcr.io/mcromio/systech-aidd-frontend:latest   Up 11 seconds (healthy)
```

### Healthcheck результаты

#### API Health Endpoint
```bash
$ curl http://89.223.67.136:8003/health
{"status":"ok"}
```
✅ **Результат:** API доступен снаружи и отвечает корректно

#### Frontend
```bash
$ curl -I http://89.223.67.136:3003/
HTTP/1.1 200 OK
```
✅ **Результат:** Frontend доступен снаружи и отвечает корректно

#### PostgreSQL
- Доступен только внутри Docker сети
- Healthcheck: `pg_isready` успешно выполняется
✅ **Результат:** База данных работает корректно

#### Bot
- Контейнер запущен и healthy
- Готов принимать сообщения через Telegram
✅ **Результат:** Bot работает корректно

## Финальный статус

### ✅ Все критерии готовности выполнены:

- [x] env.production.example содержит все переменные с комментариями
- [x] docker-compose.prod.yml настроен для портов 8003/3003
- [x] PostgreSQL не expose наружу
- [x] Volumes для промптов добавлены
- [x] manual-deploy.md содержит детальную инструкцию
- [x] Все команды готовы для copy-paste
- [x] Инструкция содержит troubleshooting секцию
- [x] План спринта создан
- [x] Все сервисы запущены на сервере
- [x] API доступен через интернет (http://89.223.67.136:8003)
- [x] Frontend доступен через интернет (http://89.223.67.136:3003)
- [x] Bot готов к работе

## Доступные URL

### Production endpoints:
- **API Documentation:** http://89.223.67.136:8003/docs
- **API Health:** http://89.223.67.136:8003/health
- **API Stats:** http://89.223.67.136:8003/stats
- **API Chat:** http://89.223.67.136:8003/chat
- **Frontend:** http://89.223.67.136:3003

### Для администрирования:
```bash
# Подключение к серверу
ssh -i <key> systech@89.223.67.136

# Переход в рабочую директорию
cd /opt/systech/rdolgovitskiy

# Проверка статуса
docker compose -f docker-compose.prod.yml ps

# Просмотр логов
docker compose -f docker-compose.prod.yml logs -f

# Перезапуск сервисов
docker compose -f docker-compose.prod.yml restart

# Остановка
docker compose -f docker-compose.prod.yml down

# Обновление образов
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## Следующие шаги

### Спринт D3: Auto Deploy
После успешного ручного развертывания D2, следующий спринт будет посвящен автоматизации:

1. Создание GitHub Actions workflow для автоматического деплоя
2. Настройка SSH ключей в GitHub Secrets
3. Автоматический деплой при push в main ветку
4. Уведомления о статусе деплоя
5. Rollback механизм

### Дополнительные рекомендации:
1. Настроить firewall (ufw) для портов 8003, 3003
2. Настроить Nginx reverse proxy с доменным именем
3. Добавить SSL сертификаты (Let's Encrypt)
4. Настроить мониторинг и алертинг
5. Настроить регулярные бэкапы PostgreSQL

## Заключение

**Спринт D2 успешно завершен!** 

Приложение развернуто на production сервере, все сервисы работают корректно и доступны через интернет. Созданы подробные инструкции для ручного развертывания, которые послужат основой для автоматизации в следующем спринте D3.

### Время выполнения:
- **Планирование:** ~30 минут
- **Создание файлов:** ~40 минут
- **Развертывание и troubleshooting:** ~31 минута
- **Итого:** ~1 час 41 минута

### Lessons Learned:
1. Важно проверять, что все файлы находятся в Git перед сборкой образов
2. Необходимо тщательно проверять маппинг портов между docker-compose и Dockerfile
3. Использование healthcheck в docker-compose критично для надежного запуска зависимых сервисов
4. Детальная инструкция по развертыванию экономит время при troubleshooting

---

**Отчет подготовлен:** 18 октября 2025
**Статус:** ✅ Спринт D2 завершен успешно

