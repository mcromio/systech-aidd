# Настройка токенов для production сервера

## Цель
Настроить реальные токены для работы Telegram Bot и OpenAI API на production сервере.

## Шаги настройки

### 1. Получить Telegram Bot Token

1. Откройте Telegram и найдите бота **@BotFather**
2. Отправьте команду `/newbot` (если создаете нового бота) или `/mybots` (если бот уже есть)
3. Следуйте инструкциям для создания бота
4. Скопируйте токен в формате: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. Получить OpenAI API Key

1. Откройте https://platform.openai.com/api-keys
2. Войдите в аккаунт OpenAI
3. Нажмите "Create new secret key"
4. Скопируйте ключ в формате: `sk-...` (показывается только один раз!)
5. **Важно:** Сохраните ключ в безопасном месте

### 3. Обновить .env на сервере

Подключитесь к серверу и отредактируйте файл `.env`:

```bash
ssh systech@89.223.67.136
cd /opt/systech/rdolgovitskiy
nano .env
```

Замените плейсхолдеры на реальные значения:

```ini
# Telegram Bot Token (от @BotFather)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# OpenAI API Key (от platform.openai.com)
OPENAI_API_KEY=sk-...

# PostgreSQL Password (установите сильный пароль)
POSTGRES_PASSWORD=your_strong_password_here
```

Сохраните файл: `Ctrl+O`, `Enter`, `Ctrl+X`

### 4. Перезапустить сервисы

```bash
cd /opt/systech/rdolgovitskiy
docker compose -f docker-compose.prod.yml restart bot
```

### 5. Проверить логи

```bash
# Проверить что бот запустился без ошибок
docker logs llm-assistant-bot --tail 20

# Должны увидеть:
# INFO | Bot запущен и готов к работе
```

## Проверка работы

### Telegram Bot

1. Найдите вашего бота в Telegram по username
2. Отправьте команду `/start`
3. Бот должен ответить приветственным сообщением

### Web Interface

1. Откройте http://89.223.67.136:3003/chat
2. Выберите диалог из списка
3. Отправьте сообщение
4. Сообщение должно появиться в истории и в Telegram

## Troubleshooting

### Bot не запускается

```bash
# Проверить токен
docker logs llm-assistant-bot --tail 30

# Если ошибка "Token is invalid!" - проверьте токен в .env
# Если ошибка "Unauthorized" - токен неправильный, получите новый от @BotFather
```

### OpenAI не отвечает

```bash
# Проверить API key
docker logs llm-assistant-bot --tail 50 | grep -i "openai"

# Если ошибка "Invalid API key" - проверьте ключ на https://platform.openai.com/api-keys
# Если ошибка "Rate limit" - превышен лимит запросов, подождите или обновите план
```

### База данных

```bash
# Проверить подключение к базе
docker exec llm-assistant-db psql -U llm_user_prod -d llm_assistant_prod -c "SELECT COUNT(*) FROM users;"

# Если ошибка "role does not exist" - проверьте POSTGRES_USER в .env и docker-compose.prod.yml
```

## Безопасность

⚠️ **ВАЖНО:**
- Никогда не коммитьте файл `.env` в Git
- Не делитесь токенами публично
- Регулярно меняйте пароли
- Используйте разные токены для dev и prod окружений

## Дополнительные настройки

### Изменить модель OpenAI

В `.env`:
```ini
OPENAI_MODEL=gpt-4o-mini  # Дешевая модель (по умолчанию)
# или
OPENAI_MODEL=gpt-4o      # Более мощная, но дороже
```

### Увеличить timeout для OpenAI

В `.env`:
```ini
OPENAI_TIMEOUT=120.0  # 2 минуты вместо 60 секунд
```

После изменений перезапустите:
```bash
docker compose -f docker-compose.prod.yml restart bot api
```

