# Инструкция по ручному развертыванию на production сервере

## Обзор

Эта инструкция описывает процесс ручного развертывания приложения на production сервере с использованием готовых Docker образов из GitHub Container Registry.

**Параметры сервера:**
- Адрес: `<server_address>` (89.223.67.136)
- Пользователь: `systech`
- Рабочая директория: `/opt/systech/rdolgovitskiy`
- Порты: API=8003, Frontend=3003, PostgreSQL=internal

**Время развертывания:** ~15-20 минут

---

## Предварительные требования

### На локальном компьютере:
- SSH ключ для доступа к серверу
- Git (для клонирования репозитория)
- Текстовый редактор

### На сервере (уже установлено):
- Docker (версия 20.10+)
- Docker Compose (версия 2.0+)
- Открыты порты: 8003 (API), 3003 (Frontend)

---

## Шаг 1: Подготовка локально

### 1.1. Клонировать репозиторий (если еще не клонирован)

```bash
git clone https://github.com/mcromio/systech-aidd.git
cd systech-aidd
git checkout devops  # или main после мерджа
```

### 1.2. Создать .env файл из шаблона

```bash
# Скопировать шаблон
cp env.production.example .env

# Отредактировать .env файл
nano .env  # или vim, code, etc.
```

**Обязательные переменные для заполнения:**

```bash
# Database (придумайте сильный пароль!)
POSTGRES_PASSWORD=<ваш_сильный_пароль>

# Telegram Bot (получите у @BotFather)
TELEGRAM_BOT_TOKEN=<ваш_токен>

# OpenAI (получите на platform.openai.com)
OPENAI_API_KEY=<ваш_ключ>

# Frontend URL (замените на IP сервера)
NEXT_PUBLIC_API_URL=http://89.223.67.136:8003
```

**Генерация сильного пароля:**
```bash
# Linux/Mac:
openssl rand -base64 24

# Windows PowerShell:
[Convert]::ToBase64String((1..24 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

### 1.3. Проверить наличие SSH ключа

```bash
# Проверить что ключ существует
ls -la ~/.ssh/id_rsa  # или другой путь к ключу

# Если ключа нет, создать новый (опционально)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

---

## Шаг 2: Подключение к серверу

### 2.1. Подключиться по SSH

```bash
# С использованием SSH ключа
ssh -i <path-to-your-key> systech@<server_address>

# Пример:
ssh -i ~/.ssh/id_rsa systech@89.223.67.136
```

**Если возникает ошибка "Permission denied":**
```bash
# Убедитесь что права на ключ корректны
chmod 600 ~/.ssh/id_rsa
```

### 2.2. Проверить Docker и Docker Compose

```bash
# Проверить версию Docker
docker --version
# Должно быть: Docker version 20.10+ или выше

# Проверить версию Docker Compose
docker compose version
# Должно быть: Docker Compose version v2.0+ или выше

# Проверить что Docker работает
docker ps
# Должен показать список контейнеров (может быть пустым)
```

---

## Шаг 3: Развертывание на сервере

### 3.1. Создать рабочую директорию

```bash
# Создать директорию для проекта
sudo mkdir -p /opt/systech/rdolgovitskiy
sudo chown -R systech:systech /opt/systech/rdolgovitskiy
cd /opt/systech/rdolgovitskiy
```

### 3.2. Скопировать файлы на сервер

**В новом терминале на локальном компьютере:**

```bash
# Перейти в директорию проекта
cd ~/path/to/systech-aidd

# Скопировать docker-compose.prod.yml
scp -i <path-to-key> docker-compose.prod.yml systech@<server_address>:/opt/systech/rdolgovitskiy/

# Скопировать .env файл
scp -i <path-to-key> .env systech@<server_address>:/opt/systech/rdolgovitskiy/

# Скопировать промпты (опционально)
scp -i <path-to-key> -r prompts systech@<server_address>:/opt/systech/rdolgovitskiy/

# Скопировать скрипт инициализации БД
scp -i <path-to-key> -r scripts systech@<server_address>:/opt/systech/rdolgovitskiy/
```

**Пример с реальным IP:**
```bash
scp -i ~/.ssh/id_rsa docker-compose.prod.yml systech@89.223.67.136:/opt/systech/rdolgovitskiy/
scp -i ~/.ssh/id_rsa .env systech@89.223.67.136:/opt/systech/rdolgovitskiy/
scp -i ~/.ssh/id_rsa -r prompts systech@89.223.67.136:/opt/systech/rdolgovitskiy/
scp -i ~/.ssh/id_rsa -r scripts systech@89.223.67.136:/opt/systech/rdolgovitskiy/
```

### 3.3. Проверить скопированные файлы

**На сервере:**

```bash
# Вернуться в терминал на сервере
cd /opt/systech/rdolgovitskiy

# Проверить что файлы скопированы
ls -la

# Должны быть:
# - docker-compose.prod.yml
# - .env
# - prompts/ (опционально)
# - scripts/

# Установить правильные права на .env
chmod 600 .env

# Проверить содержимое .env (убедиться что секреты заполнены)
head -20 .env
```

### 3.4. Загрузить Docker образы

```bash
# Pull всех образов из GitHub Container Registry
docker compose -f docker-compose.prod.yml pull

# Этот процесс может занять 2-5 минут в зависимости от скорости интернета

# Проверить что образы загружены
docker images | grep systech-aidd
```

**Ожидаемый вывод:**
```
ghcr.io/mcromio/systech-aidd-bot          latest    ...   ...   ...
ghcr.io/mcromio/systech-aidd-api          latest    ...   ...   ...
ghcr.io/mcromio/systech-aidd-frontend     latest    ...   ...   ...
```

### 3.5. Запустить все сервисы

```bash
# Запустить в фоновом режиме
docker compose -f docker-compose.prod.yml up -d

# Процесс запуска займет 1-2 минуты
```

**Ожидаемый вывод:**
```
[+] Running 5/5
 ✔ Network rdolgovitskiy_llm-network        Created
 ✔ Volume "rdolgovitskiy_postgres_data"    Created
 ✔ Container llm-assistant-db               Healthy
 ✔ Container llm-assistant-api              Healthy
 ✔ Container llm-assistant-bot              Started
 ✔ Container llm-assistant-frontend         Started
```

---

## Шаг 4: Проверка работоспособности

### 4.1. Проверить статус контейнеров

```bash
# Посмотреть статус всех контейнеров
docker compose -f docker-compose.prod.yml ps

# Должны быть все 4 сервиса в состоянии "Up" или "Up (healthy)"
```

**Ожидаемый вывод:**
```
NAME                      IMAGE                                      STATUS
llm-assistant-api         ghcr.io/mcromio/systech-aidd-api:latest    Up (healthy)
llm-assistant-bot         ghcr.io/mcromio/systech-aidd-bot:latest    Up
llm-assistant-db          postgres:17-alpine                         Up (healthy)
llm-assistant-frontend    ghcr.io/mcromio/systech-aidd-frontend      Up
```

### 4.2. Проверить логи

```bash
# Логи всех сервисов
docker compose -f docker-compose.prod.yml logs -f

# Ctrl+C для выхода

# Логи конкретного сервиса
docker compose -f docker-compose.prod.yml logs -f bot
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f postgres

# Последние 50 строк
docker compose -f docker-compose.prod.yml logs --tail=50
```

**Что искать в логах:**
- ✅ Bot: "Bot started successfully", "Polling started"
- ✅ API: "Uvicorn running on http://0.0.0.0:8003"
- ✅ Frontend: "Ready in X ms", "started server on 0.0.0.0:3000"
- ✅ PostgreSQL: "database system is ready to accept connections"

### 4.3. Проверить healthcheck API (на сервере)

```bash
# Проверка через localhost
curl http://localhost:8003/health

# Должен вернуть: {"status":"ok"}
```

### 4.4. Проверить доступность снаружи

**С локального компьютера (или через браузер):**

```bash
# Проверить API
curl http://89.223.67.136:8003/health

# Должен вернуть: {"status":"ok"}
```

**Через браузер:**

1. **API Documentation:**
   ```
   http://89.223.67.136:8003/docs
   ```
   Должна открыться Swagger UI с документацией API

2. **Frontend:**
   ```
   http://89.223.67.136:3003
   ```
   Должна открыться главная страница приложения

3. **Dashboard:**
   ```
   http://89.223.67.136:3003/dashboard
   ```
   Должна показаться статистика (может быть пустая изначально)

### 4.5. Тестирование Telegram бота

1. Откройте Telegram
2. Найдите вашего бота по username (который был получен от @BotFather)
3. Нажмите `/start`
4. Отправьте тестовое сообщение, например: "Привет!"
5. Бот должен ответить

**Проверка в логах:**
```bash
docker compose -f docker-compose.prod.yml logs -f bot

# Должны быть сообщения о получении и обработке команд
```

---

## Шаг 5: Управление сервисами

### Основные команды

```bash
# Остановить все сервисы
docker compose -f docker-compose.prod.yml down

# Запустить все сервисы
docker compose -f docker-compose.prod.yml up -d

# Перезапустить конкретный сервис
docker compose -f docker-compose.prod.yml restart bot
docker compose -f docker-compose.prod.yml restart api
docker compose -f docker-compose.prod.yml restart frontend

# Перезапустить все сервисы
docker compose -f docker-compose.prod.yml restart

# Просмотр логов в реальном времени
docker compose -f docker-compose.prod.yml logs -f

# Обновить образы до последней версии
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Статус и мониторинг

```bash
# Статус контейнеров
docker compose -f docker-compose.prod.yml ps

# Использование ресурсов
docker stats

# Информация о контейнере
docker inspect llm-assistant-bot

# Выполнить команду внутри контейнера
docker exec -it llm-assistant-api bash
```

---

## Troubleshooting

### Проблема 1: Контейнер постоянно перезапускается

**Симптомы:**
```bash
docker compose ps
# STATUS: Restarting
```

**Решение:**
```bash
# Посмотреть логи для определения причины
docker compose -f docker-compose.prod.yml logs <service-name>

# Типичные причины:
# 1. Неправильные переменные окружения (.env)
# 2. База данных не готова (проверьте postgres логи)
# 3. Неверный TELEGRAM_BOT_TOKEN или OPENAI_API_KEY
```

### Проблема 2: База данных не запускается

**Симптомы:**
```bash
docker compose logs postgres
# Error: could not create directory
```

**Решение:**
```bash
# Проверить права на volume
docker volume inspect rdolgovitskiy_postgres_data

# Удалить volume и пересоздать (ОСТОРОЖНО! Удалит все данные)
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d
```

### Проблема 3: Порты уже заняты

**Симптомы:**
```bash
Error: bind: address already in use
```

**Решение:**
```bash
# Проверить что использует порт
sudo lsof -i :8003
sudo lsof -i :3003

# Остановить конфликтующий процесс
sudo kill -9 <PID>

# Или изменить порты в docker-compose.prod.yml
```

### Проблема 4: Cannot pull образы (Permission denied)

**Симптомы:**
```bash
Error: pull access denied
```

**Решение:**
```bash
# Образы должны быть публичными в GitHub Container Registry
# Проверьте: https://github.com/users/mcromio/packages

# Убедитесь что packages имеют visibility: Public
```

### Проблема 5: API возвращает 502 Bad Gateway

**Причины:**
- API контейнер не запущен или не healthy
- Неверный DATABASE_URL

**Решение:**
```bash
# Проверить статус API
docker compose -f docker-compose.prod.yml ps api

# Проверить логи API
docker compose -f docker-compose.prod.yml logs api

# Проверить healthcheck
curl http://localhost:8003/health

# Перезапустить API
docker compose -f docker-compose.prod.yml restart api
```

### Проблема 6: Frontend показывает ошибку соединения с API

**Причина:** Неверный NEXT_PUBLIC_API_URL

**Решение:**
```bash
# Проверить .env файл
cat .env | grep NEXT_PUBLIC_API_URL

# Должно быть:
# NEXT_PUBLIC_API_URL=http://89.223.67.136:8003

# Изменить и перезапустить
nano .env
docker compose -f docker-compose.prod.yml restart frontend
```

### Проблема 7: Telegram бот не отвечает

**Решение:**
```bash
# Проверить логи бота
docker compose -f docker-compose.prod.yml logs -f bot

# Проверить токен
cat .env | grep TELEGRAM_BOT_TOKEN

# Проверить что бот запущен
docker compose -f docker-compose.prod.yml ps bot

# Перезапустить бота
docker compose -f docker-compose.prod.yml restart bot
```

---

## Полезные команды для диагностики

```bash
# Проверить все переменные окружения контейнера
docker inspect llm-assistant-bot | grep -A 50 "Env"

# Проверить сеть
docker network ls
docker network inspect rdolgovitskiy_llm-network

# Проверить volumes
docker volume ls
docker volume inspect rdolgovitskiy_postgres_data

# Проверить размер образов
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Очистить неиспользуемые ресурсы
docker system prune -a
```

---

## Безопасность

### Рекомендации:

1. **Защитите .env файл:**
   ```bash
   chmod 600 .env
   ```

2. **Регулярно обновляйте образы:**
   ```bash
   docker compose -f docker-compose.prod.yml pull
   docker compose -f docker-compose.prod.yml up -d
   ```

3. **Настройте firewall:**
   ```bash
   sudo ufw allow 8003/tcp
   sudo ufw allow 3003/tcp
   sudo ufw enable
   ```

4. **Бэкап базы данных:**
   ```bash
   # Создать бэкап
   docker exec llm-assistant-db pg_dump -U llm_user_prod llm_assistant_prod > backup.sql

   # Восстановить из бэкапа
   docker exec -i llm-assistant-db psql -U llm_user_prod llm_assistant_prod < backup.sql
   ```

5. **Мониторинг логов:**
   ```bash
   # Настроить ротацию логов
   docker compose -f docker-compose.prod.yml logs --since 24h > daily-logs.txt
   ```

---

## Следующие шаги

После успешного развертывания:

1. ✅ Проверить работу всех сервисов
2. ✅ Протестировать Telegram бота
3. ✅ Проверить доступность API и Frontend через интернет
4. 📝 Документировать любые проблемы и их решения
5. 🔄 Подготовиться к Спринту D3: Автоматизация деплоя через GitHub Actions

---

## Контакты и поддержка

- Документация проекта: `docs/`
- Roadmap: `devops/doc/devops-roadmap.md`
- Issues: https://github.com/mcromio/systech-aidd/issues

