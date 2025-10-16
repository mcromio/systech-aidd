# 📖 Getting Started - Быстрый старт за 15 минут

> Запустите проект с нуля и отправьте первое сообщение боту

---

## ✅ Prerequisites

Перед началом убедитесь что у вас есть:

- **Python 3.12+** ([скачать](https://www.python.org/downloads/))
- **uv** - менеджер зависимостей ([установка](https://docs.astral.sh/uv/))
- **Git** - для клонирования репозитория
- **Telegram Bot Token** - создайте через [@BotFather](https://t.me/botfather)
- **OpenAI API Key** - получите на [platform.openai.com](https://platform.openai.com)
- **OpenAI Proxy URL** - если нужен (опционально)

---

## 🚀 Шаг 1: Клонирование и установка (5 мин)

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd systech-aidd_mcr

# 2. Установить зависимости
uv sync

# Вывод должен быть примерно таким:
# Resolved 50 packages in 2.5s
# Installed 50 packages in 1.2s
```

**✅ Проверка:**
```bash
uv --version
# Output: uv 0.x.x

python --version
# Output: Python 3.12.x
```

---

## ⚙️ Шаг 2: Настройка конфигурации (5 мин)

### Создать .env файл

```bash
# Создать из шаблона
cp .env.example .env

# Открыть в редакторе
nano .env
```

### Заполнить обязательные параметры

```bash
# .env файл
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_PROXY_URL=https://api.your-proxy.com/v1
OPENAI_MODEL=gpt-4o-mini

# Роль бота
SYSTEM_PROMPT_FILE=prompts/default.txt
ROLE_NAME=AI Assistant
ROLE_DESCRIPTION=Универсальный ИИ-ассистент

# Параметры
MAX_CONTEXT_MESSAGES=10
LOG_LEVEL=INFO
```

**⚠️ Важно:**
- `TELEGRAM_BOT_TOKEN` - получите от @BotFather
- `OPENAI_API_KEY` - ваш ключ OpenAI
- `OPENAI_PROXY_URL` - URL прокси для доступа к OpenAI API

**✅ Проверка конфигурации:**
```bash
python -c "from src.config import Config; c=Config(); print('✓ Config OK')"
# Output: ✓ Config OK
```

---

## 🧪 Шаг 3: Запуск тестов (2 мин)

Убедимся что всё работает:

```bash
make test
```

**Ожидаемый результат:**
```
========================= 55 passed in 2.50s =========================
src/__init__.py                  100%
src/config.py                     96%
src/context_manager.py           100%
src/handlers.py                   93%
...
TOTAL                             78%
```

**✅ Все тесты прошли** → можно запускать бота

---

## 🤖 Шаг 4: Запуск бота (3 мин)

```bash
make run
```

**Вывод при успешном запуске:**
```
2025-10-16 14:23:15 | INFO     | __main__ | === Запуск LLM-ассистента ===
2025-10-16 14:23:15 | INFO     | __main__ | Модель: gpt-4o-mini
2025-10-16 14:23:15 | INFO     | __main__ | Макс. контекст: 10
2025-10-16 14:23:16 | INFO     | src.bot | Бот запущен: @your_bot_name
2025-10-16 14:23:16 | INFO     | aiogram.dispatcher | Start polling
```

**✅ Бот запущен!** Оставьте терминал открытым.

---

## 💬 Шаг 5: Первое общение с ботом (3 мин)

Откройте Telegram и найдите вашего бота по имени `@your_bot_name`

### Тестовые команды

```
1️⃣ /start
Ожидаемый ответ: Приветствие

2️⃣ /role
Ожидаемый ответ:
🤖 Моя роль

Название: AI Assistant
Описание: Универсальный ИИ-ассистент
...

3️⃣ /help
Ожидаемый ответ: Список доступных команд

4️⃣ Привет!
Ожидаемый ответ: LLM ответит на ваше сообщение

5️⃣ Кто такой Пушкин?
Ожидаемый ответ: LLM использует Wikipedia и даст информацию

6️⃣ /reset
Ожидаемый ответ: История диалога очищена
```

**✅ Если всё работает** - поздравляю, проект запущен! 🎉

---

## 🔍 Быстрая диагностика

### Бот не отвечает?

```bash
# Проверить логи в терминале
# Должны быть строки вида:
# INFO | src.handlers | Сообщение от пользователя 123456...
```

### Ошибка "TELEGRAM_BOT_TOKEN not found"?

```bash
# Проверить что .env файл существует
ls -la .env

# Проверить содержимое
cat .env | grep TELEGRAM_BOT_TOKEN
```

### Ошибка "OpenAI API timeout"?

```bash
# Проверить прокси URL
cat .env | grep OPENAI_PROXY_URL

# Проверить что прокси доступен
curl -I https://api.your-proxy.com/v1
```

**Больше решений:** [10_troubleshooting.md](10_troubleshooting.md)

---

## 📚 Что дальше?

### Для разработчиков

1. **Изучить структуру:** [05_codebase_tour.md](05_codebase_tour.md)
2. **Понять архитектуру:** [02_architecture_overview.md](02_architecture_overview.md)
3. **Настроить свою роль:** [06_configuration.md](06_configuration.md)
4. **Начать разработку:** [07_development_workflow.md](07_development_workflow.md)

### Для DevOps

1. **Настроить конфигурацию:** [06_configuration.md](06_configuration.md)
2. **Изучить деплой:** [09_deployment.md](09_deployment.md)

---

## 🛑 Остановка бота

```bash
# В терминале с ботом нажать:
Ctrl + C

# Вывод:
# INFO | __main__ | Бот остановлен пользователем
```

---

## ⚡ Makefile команды

```bash
make help          # Список всех команд
make run           # Запустить бота
make test          # Запустить тесты
make lint          # Проверить код линтером
make format        # Отформатировать код
make clean         # Очистить кэш
```

---

## ✅ Чек-лист успешного старта

- [ ] Python 3.12+ установлен
- [ ] uv установлен
- [ ] Репозиторий склонирован
- [ ] `uv sync` выполнен успешно
- [ ] `.env` файл создан и заполнен
- [ ] Тесты проходят (`make test`)
- [ ] Бот запускается (`make run`)
- [ ] Бот отвечает на `/start` в Telegram
- [ ] Бот отвечает на обычные сообщения
- [ ] Wikipedia tool работает

---

**Готово! Теперь вы можете работать с проектом.** 🚀

**Следующий шаг:** [05_codebase_tour.md](05_codebase_tour.md) - изучите структуру кода


