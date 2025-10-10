# Task List - LLM Assistant Bot

> Пошаговый план разработки с тестируемыми итерациями  
> Принцип: каждая итерация = работающий код + тесты

---

## 📊 Отчет о прогрессе

| Итерация | Описание | Статус | Тесты | Дата |
|----------|----------|--------|-------|------|
| **Iter 1** | Базовая структура + Config | ✅ DONE | ✅ | 2025-10-10 |
| **Iter 2** | ContextManager | ✅ DONE | ✅ | 2025-10-10 |
| **Iter 3** | WikipediaTool | ✅ DONE | ✅ | 2025-10-10 |
| **Iter 4** | LLMClient (базовый) | ✅ DONE | ✅ | 2025-10-10 |
| **Iter 5** | Function Calling | 🔲 TODO | 🔲 | - |
| **Iter 6** | Telegram Bot | 🔲 TODO | 🔲 | - |
| **Iter 7** | Полная интеграция | 🔲 TODO | 🔲 | - |
| **Iter 8** | Docker + финализация | 🔲 TODO | 🔲 | - |

### Легенда статусов
- 🔲 TODO - не начато
- 🔄 IN PROGRESS - в работе
- ✅ DONE - завершено
- ❌ BLOCKED - заблокировано

---

## Iteration 1: Базовая структура + Config

**Цель:** Создать структуру проекта и конфигурацию  
**Тест:** Загрузка и валидация .env файла

### Задачи

- [x] Создать структуру директорий (`src/`, `tests/`)
- [x] Создать `pyproject.toml` с зависимостями
- [x] Запустить `uv sync` для создания `uv.lock`
- [x] Создать `Makefile` с командами
- [x] Реализовать `src/__init__.py`
- [x] Реализовать `src/config.py` (Pydantic Config)
- [x] Написать `tests/test_config.py`
- [x] Проверить: `make test` проходит

### Критерий готовности
```bash
# Проверка uv
uv sync
# Должен создать uv.lock и установить зависимости

# Проверка конфигурации
python -c "from src.config import Config; c=Config(); print(c.telegram_bot_token[:10])"
# Вывод: 8248434371
```

---

## Iteration 2: ContextManager

**Цель:** Управление историей диалогов  
**Тест:** Добавление/получение/очистка истории

### Задачи

- [x] Реализовать `src/context_manager.py`
- [x] Создать Pydantic модели `Message`, `UserContext`
- [x] Реализовать методы: `add_message`, `get_history`, `clear_history`
- [x] Написать `tests/test_context_manager.py`
- [x] Проверить: тесты проходят, coverage > 80%

### Критерий готовности
```python
from src.context_manager import ContextManager
manager = ContextManager(config)
manager.add_message(123, "user", "Hello")
assert len(manager.get_history(123)) == 1
```

---

## Iteration 3: WikipediaTool

**Цель:** Поиск информации в Wikipedia  
**Тест:** Поиск реальной статьи

### Задачи

- [x] Реализовать `src/wikipedia_tool.py`
- [x] Методы: `__init__`, `search`
- [x] Обработка ошибок (статья не найдена)
- [x] Написать `tests/test_wikipedia_tool.py`
- [x] Проверить: поиск "Python" возвращает результат

### Критерий готовности
```python
from src.wikipedia_tool import WikipediaTool
tool = WikipediaTool()
result = await tool.search("Python", "ru")
assert "Python" in result
assert len(result) > 0
```

---

## Iteration 4: LLMClient (базовый)

**Цель:** Базовая интеграция с OpenAI (без tools)  
**Тест:** Получение ответа от LLM

### Задачи

- [x] Реализовать `src/llm_client.py` (без function calling)
- [x] Метод `get_response` (базовая версия)
- [x] Инициализация `AsyncOpenAI` с прокси
- [x] Обработка ошибок API
- [x] Написать `tests/test_llm_client.py` (с моками)
- [x] Проверить: mock тесты проходят

### Критерий готовности
```python
from src.llm_client import LLMClient
client = LLMClient(config, None)
response = await client.get_response([Message(role="user", content="Hello")])
assert response is not None
```

---

## Iteration 5: Function Calling

**Цель:** Интеграция Wikipedia через function calling  
**Тест:** LLM использует Wikipedia tool

### Задачи

- [ ] Добавить `_get_tools_schema()` в LLMClient
- [ ] Добавить `_execute_tool()` в LLMClient
- [ ] Реализовать цикл обработки tool calls (макс 5 итераций)
- [ ] Интегрировать WikipediaTool
- [ ] Обновить тесты с tool calls
- [ ] Проверить: тест с Wikipedia работает

### Критерий готовности
```python
# Запрос "Кто такой Пушкин?" должен вызвать Wikipedia tool
client = LLMClient(config, wikipedia_tool)
response = await client.get_response([Message(role="user", content="Кто такой Пушкин?")])
assert "Пушкин" in response or "поэт" in response.lower()
```

---

## Iteration 6: Telegram Bot

**Цель:** Базовый Telegram бот с командами  
**Тест:** Бот отвечает на команды

### Задачи

- [ ] Реализовать `src/handlers.py` (MessageHandler)
- [ ] Методы: `handle_start`, `handle_help`, `handle_reset`, `handle_message`
- [ ] Реализовать `src/bot.py` (TelegramBot)
- [ ] Регистрация handlers в диспетчере
- [ ] Реализовать `src/main.py` (точка входа)
- [ ] Настройка логирования
- [ ] Написать `tests/test_handlers.py`
- [ ] Проверить: бот запускается локально

### Критерий готовности
```bash
make run
# В Telegram отправить /start боту
# Бот должен ответить приветствием
```

**Ручное тестирование:**
1. `/start` → приветствие
2. `/help` → справка
3. `/reset` → подтверждение очистки
4. `Привет!` → ответ от LLM
5. `Кто такой Пушкин?` → ответ с использованием Wikipedia

---

## Iteration 7: Полная интеграция

**Цель:** Все компоненты работают вместе  
**Тест:** E2E сценарии

### Задачи

- [ ] Интеграционные тесты (все компоненты)
- [ ] Тест: диалог с контекстом (несколько сообщений)
- [ ] Тест: использование Wikipedia в диалоге
- [ ] Тест: команда /reset очищает контекст
- [ ] Проверка обработки ошибок (API недоступен)
- [ ] Проверка лимитов (MAX_CONTEXT_MESSAGES)
- [ ] Проверить: coverage > 70%

### Критерий готовности
```bash
uv sync  # Обновить зависимости если нужно
make test
# Все тесты проходят, coverage > 70%

make run
# Протестировать все сценарии из vision.md раздел 7
```

**E2E сценарии:**
1. Длинный диалог (> 10 сообщений) → старые сообщения удаляются
2. Вопрос про Wikipedia → корректный ответ
3. Последовательные вопросы → контекст сохраняется
4. `/reset` → контекст очищен
5. Ошибка API → пользователь видит сообщение об ошибке

---

## Iteration 8: Docker + финализация

**Цель:** Контейнеризация и документация  
**Тест:** Бот работает в Docker

### Задачи

- [ ] Создать `Dockerfile` (multi-stage)
- [ ] Создать `docker-compose.yml`
- [ ] Создать `.dockerignore`
- [ ] Обновить Makefile (docker команды)
- [ ] Создать `README.md` с инструкциями
- [ ] Создать `CHANGELOG.md`
- [ ] Проверить: бот работает в Docker
- [ ] Финальное тестирование

### Критерий готовности
```bash
make docker-build
make docker-up
make docker-logs
# Бот работает, логи корректные

# В Telegram протестировать все функции
```

**Финальная проверка:**
- [ ] Бот запускается локально (`make run`)
- [ ] Бот запускается в Docker (`make docker-up`)
- [ ] Все команды работают (`/start`, `/help`, `/reset`)
- [ ] LLM отвечает на вопросы
- [ ] Wikipedia tool работает
- [ ] Контекст сохраняется
- [ ] Логи выводятся корректно
- [ ] Тесты проходят (`make test`)
- [ ] Документация полная (README, CHANGELOG)

---

## 🎯 Definition of Done для каждой итерации

Итерация считается завершенной, если:

1. ✅ **Код написан** - все файлы созданы согласно tasks
2. ✅ **Type hints** - везде есть аннотации типов (обязательно!)
3. ✅ **Docstrings** - все публичные методы документированы на русском
4. ✅ **Логирование** - используется logging, не print()
5. ✅ **Нет дублирования** - код следует принципу DRY (Don't Repeat Yourself)
6. ✅ **Методы короткие** - максимум 30-40 строк, иначе разбить
7. ✅ **Тесты написаны** - юнит-тесты покрывают функционал
8. ✅ **Тесты проходят** - `make test` без ошибок
9. ✅ **Линтер проходит** - `make lint` без ошибок
10. ✅ **Критерий готовности** - код из "Критерий готовности" работает
11. ✅ **Ручное тестирование** - функционал проверен вручную (где применимо)

---

## 📝 Шаблон обновления отчета

После завершения итерации обновите таблицу:

```markdown
| **Iter N** | Описание | ✅ DONE | ✅ | 2025-10-11 |
```

Где:
- Статус: 🔲 → 🔄 → ✅
- Тесты: 🔲 → ✅
- Дата: дата завершения

---

## 🚀 Быстрый старт разработки

```bash
# 1. Настройка окружения
uv sync  # Установка всех зависимостей
make setup

# 2. Запуск разработки (для каждой итерации)
make format  # Форматирование кода
make lint    # Проверка линтером
make test    # Запуск тестов

# 3. Локальный запуск бота
make run

# 4. Docker (для итерации 8)
make docker-build
make docker-up
make docker-logs
```

---

## 📚 Ссылки

- [vision.md](vision.md) - техническое видение
- [conventions.md](conventions.md) - правила разработки
- [idea.md](idea.md) - концепция проекта

---

**Версия**: 1.0  
**Дата создания**: 10 октября 2025  
**Статус**: 🔲 TODO - готово к началу разработки

