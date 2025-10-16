# ⚙️ Configuration - Конфигурация и секреты

> Как настроить проект под свои нужды

---

## 📋 Обзор

Вся конфигурация хранится в `.env` файле и загружается через Pydantic.

---

## 🔐 Создание .env файла

```bash
# 1. Создать из шаблона
cp .env.example .env

# 2. Открыть в редакторе
nano .env
```

---

## ⚡ Обязательные параметры

### Telegram Bot

```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Как получить:**
1. Открыть [@BotFather](https://t.me/botfather) в Telegram
2. Отправить `/newbot`
3. Следовать инструкциям
4. Скопировать полученный токен

---

### OpenAI API

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_PROXY_URL=https://api.your-proxy.com/v1
```

**Как получить:**
- **API Key:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Proxy URL:** URL вашего прокси-сервера для доступа к OpenAI API

**⚠️ Важно:** Без прокси может не работать в некоторых регионах

---

## 🎨 Настройка роли бота

### Роль из готового промпта

```bash
# Выбрать один из готовых промптов
SYSTEM_PROMPT_FILE=prompts/default.txt
ROLE_NAME=AI Assistant
ROLE_DESCRIPTION=Универсальный ИИ-ассистент
```

**Доступные промпты:**
- `prompts/default.txt` - универсальный ассистент
- `prompts/it_consultant.txt` - IT-консультант
- `prompts/personal_assistant.txt` - персональный помощник
- `prompts/python_tutor.txt` - учитель Python

---

### Создать свою роль

**1. Создать файл промпта:**

```bash
# Создать файл
nano prompts/my_custom_role.txt
```

```txt
Ты профессиональный копирайтер.

Твоя роль:
- Писать продающие тексты
- Создавать заголовки и слоганы
- Редактировать текст
- Давать советы по стилю

Стиль: креативный, убедительный, без клише.
```

**2. Обновить .env:**

```bash
SYSTEM_PROMPT_FILE=prompts/my_custom_role.txt
ROLE_NAME=Copywriter Pro
ROLE_DESCRIPTION=Профессиональный копирайтер
```

**3. Перезапустить бота:**

```bash
make run
```

**4. Проверить:**

```
/role
# Вывод:
# 🤖 Моя роль
# Название: Copywriter Pro
# Описание: Профессиональный копирайтер
```

---

## 🎛️ Опциональные параметры

### OpenAI настройки

```bash
# Модель LLM
OPENAI_MODEL=gpt-4o-mini
# Доступно: gpt-4o-mini, gpt-4o, gpt-4-turbo, gpt-3.5-turbo

# Timeout для запросов (секунды)
OPENAI_TIMEOUT=30.0
```

---

### Лимиты

```bash
# Максимум сообщений в истории диалога
MAX_CONTEXT_MESSAGES=10
# Диапазон: 1-50, default: 10

# Максимум итераций tool calling
MAX_TOOL_ITERATIONS=10
# Диапазон: 1-20, default: 10

# Максимум веб-поисков за диалог
MAX_WEBSEARCH_CALLS=2
# Диапазон: 1-5, default: 2

# Максимум токенов в ответе
MAX_COMPLETION_TOKENS=10000
# Диапазон: 1000-100000, default: 10000
```

---

### Логирование

```bash
# Уровень логирования
LOG_LEVEL=INFO
# Доступно: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**DEBUG** - детальные логи для отладки
**INFO** - основные события (default)
**WARNING** - предупреждения
**ERROR** - только ошибки

---

## 📝 Полный пример .env

```bash
# === ОБЯЗАТЕЛЬНЫЕ ===

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_PROXY_URL=https://api.your-proxy.com/v1

# === РОЛЬ БОТА ===

SYSTEM_PROMPT_FILE=prompts/default.txt
ROLE_NAME=AI Assistant
ROLE_DESCRIPTION=Универсальный ИИ-ассистент

# === ОПЦИОНАЛЬНЫЕ ===

# OpenAI настройки
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30.0

# Лимиты
MAX_CONTEXT_MESSAGES=10
MAX_TOOL_ITERATIONS=10
MAX_WEBSEARCH_CALLS=2
MAX_COMPLETION_TOKENS=10000

# Логирование
LOG_LEVEL=INFO
```

---

## 🔒 Безопасность секретов

### ✅ Правильно

```bash
# .env файл в .gitignore
echo ".env" >> .gitignore

# Никогда не коммитить токены
git add .
git commit -m "..."
# .env автоматически игнорируется
```

### ❌ Неправильно

```bash
# НЕ коммитить .env
git add .env  # ❌ Плохо!

# НЕ хардкодить токены в коде
TELEGRAM_BOT_TOKEN = "123:ABC"  # ❌ Плохо!
```

---

## 🧪 Проверка конфигурации

### Валидация Config

```bash
# Проверить что Config загружается
python -c "from src.config import Config; c=Config(); print('✓ Config OK')"
```

**Ошибки валидации:**

```python
# Если параметр отсутствует
# ValidationError: Field required

# Если параметр неверного типа
MAX_CONTEXT_MESSAGES=abc
# ValidationError: Input should be a valid integer

# Если параметр вне диапазона
MAX_CONTEXT_MESSAGES=100
# ValidationError: Input should be less than or equal to 50
```

---

## 🔧 Разные окружения

### Local (разработка)

```bash
# .env.local
OPENAI_MODEL=gpt-4o-mini  # Дешевая модель
LOG_LEVEL=DEBUG           # Детальные логи
MAX_CONTEXT_MESSAGES=5    # Небольшой контекст
```

### Production

```bash
# .env.production
OPENAI_MODEL=gpt-4o       # Лучшая модель
LOG_LEVEL=INFO            # Основные логи
MAX_CONTEXT_MESSAGES=10   # Полный контекст
```

**Переключение:**

```bash
# Local
cp .env.local .env
make run

# Production
cp .env.production .env
make run
```

---

## 🐳 Docker конфигурация

### Через .env файл

```yaml
# docker-compose.yml
services:
  bot:
    env_file: .env
```

### Через переменные окружения

```yaml
# docker-compose.yml
services:
  bot:
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

---

## 🔍 Отладка конфигурации

### Проверить загруженные значения

```bash
python -c "
from src.config import Config
c = Config()
print(f'Model: {c.openai_model}')
print(f'Max context: {c.max_context_messages}')
print(f'Role: {c.role_name}')
print(f'Prompt length: {len(c.system_prompt)} chars')
"
```

### Проверить системный промпт

```bash
python -c "
from src.config import Config
c = Config()
print(c.system_prompt[:200])
"
```

---

## ❓ FAQ

**Q: Где хранить .env?**
A: В корне проекта, НЕ коммитить в git

**Q: Можно ли использовать переменные окружения напрямую?**
A: Да, Pydantic читает из environment variables

**Q: Как часто обновляется конфигурация?**
A: При каждом запуске бота (нужен перезапуск)

**Q: Можно ли менять роль без перезапуска?**
A: Нет, нужен перезапуск (`Ctrl+C` → `make run`)

---

## 📚 Дополнительно

**Getting Started:** [01_getting_started.md](01_getting_started.md)
**Модель данных:** [03_data_model.md](03_data_model.md)
**Troubleshooting:** [10_troubleshooting.md](10_troubleshooting.md)


