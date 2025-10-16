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
| **Iter 5** | Function Calling | ✅ DONE | ✅ | 2025-10-10 |
| **Iter 6** | Telegram Bot | ✅ DONE | ✅ | 2025-10-10 |
| **Iter 7** | Команда /role (TDD) | ✅ DONE | ✅ | 2025-10-11 |
| **Iter 8** | Полная интеграция | 🔲 TODO | 🔲 | - |
| **Iter 9** | Docker + финализация | 🔲 TODO | 🔲 | - |

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

- [x] Добавить `_get_tools_schema()` в LLMClient
- [x] Добавить `_execute_tool()` в LLMClient
- [x] Реализовать цикл обработки tool calls (макс 5 итераций)
- [x] Интегрировать WikipediaTool
- [x] Обновить тесты с tool calls
- [x] Проверить: тест с Wikipedia работает

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

- [x] Реализовать `src/handlers.py` (MessageHandler)
- [x] Методы: `handle_start`, `handle_help`, `handle_reset`, `handle_message`
- [x] Реализовать `src/bot.py` (TelegramBot)
- [x] Регистрация handlers в диспетчере
- [x] Реализовать `src/main.py` (точка входа)
- [x] Настройка логирования
- [x] Написать `tests/test_handlers.py`
- [x] Проверить: бот запускается локально

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

## Iteration 7: Команда /role (TDD)

**Цель:** Реализовать команду `/role` для отображения роли бота (ИИ-продукт с ролью)
**Тест:** TDD цикл - RED → GREEN → REFACTOR
**Подход:** Test-Driven Development

### TDD План реализации

#### 🔴 RED Phase: Падающие тесты

**1. Тесты для Config:**
- Загрузка системного промпта из файла
- Валидация наличия файла промпта
- Корректная обработка role_name и role_description

**2. Тесты для команды /role:**
- Отображение названия роли
- Отображение описания роли
- Форматирование ответа

### Задачи (TDD цикл)

#### 🔴 RED: Написать падающие тесты

- [ ] Создать директорию `prompts/`
- [ ] Создать `prompts/default.txt` с дефолтным промптом
- [ ] Обновить `tests/test_config.py`:
  - [ ] `test_config_loads_system_prompt_from_file` - загрузка промпта
  - [ ] `test_config_raises_error_if_prompt_file_missing` - ошибка при отсутствии файла
  - [ ] `test_config_has_role_name_and_description` - проверка полей роли
- [ ] Обновить `tests/test_handlers.py`:
  - [ ] `test_handle_role_returns_role_info` - команда /role возвращает инфо о роли
  - [ ] `test_handle_role_includes_role_name` - в ответе есть название
  - [ ] `test_handle_role_includes_role_description` - в ответе есть описание
- [ ] Запустить `pytest tests/` → должны упасть ❌

#### 🟢 GREEN: Минимальный код для прохождения тестов

- [ ] Обновить `src/config.py`:
  - [ ] Добавить поля: `system_prompt_file`, `role_name`, `role_description`
  - [ ] Добавить метод `model_post_init()` для загрузки промпта из файла
  - [ ] Обновить валидацию
- [ ] Обновить `src/handlers.py`:
  - [ ] Добавить метод `handle_role()` для команды /role
  - [ ] Зарегистрировать handler в `src/bot.py`
- [ ] Запустить `pytest tests/` → должны пройти ✅

#### 🔵 REFACTOR: Улучшение кода

- [ ] Создать дополнительные примеры промптов:
  - [ ] `prompts/it_consultant.txt`
  - [ ] `prompts/personal_assistant.txt`
  - [ ] `prompts/python_tutor.txt`
- [ ] Улучшить форматирование ответа команды /role (эмодзи, структура)
- [ ] Добавить логирование загрузки промпта
- [ ] Убедиться что тесты остаются зелеными ✅

#### Финальная проверка

- [ ] `make format` - форматирование
- [ ] `make lint` - линтер без ошибок
- [ ] `make test` - все тесты проходят
- [ ] Coverage для новых файлов >= 80%

### Критерий готовности

**TDD проверка:**

```bash
# 1. Проверка Config с загрузкой промпта
python -c "
from src.config import Config
c = Config()
print(f'Role: {c.role_name}')
print(f'Description: {c.role_description}')
print(f'Prompt loaded: {len(c.system_prompt) > 0}')
"
# Вывод:
# Role: AI Assistant
# Description: Универсальный ИИ-ассистент
# Prompt loaded: True

# 2. Проверка тестов
pytest tests/test_config.py -v
pytest tests/test_handlers.py::test_handle_role -v
# Все тесты должны проходить ✅

# 3. Проверка coverage
pytest tests/ --cov=src --cov-report=term
# Coverage >= 80%
```

**Ручное тестирование:**

```bash
make run
# В Telegram отправить боту: /role
# Ожидаемый ответ:
# 🤖 Моя роль
#
# Название: AI Assistant
#
# Описание: Универсальный ИИ-ассистент
#
# Я специализируюсь на выполнении конкретных задач в рамках своей роли.
# Системный промпт: prompts/default.txt
```

### Примеры промптов для создания

#### prompts/default.txt
```
Ты универсальный ИИ-ассистент.

Твоя роль:
- Помогать пользователям с различными вопросами
- Предоставлять точную и полезную информацию
- Быть вежливым и профессиональным

Отвечай четко, по существу. Используй доступные инструменты (Wikipedia) когда нужна фактическая информация.
```

#### prompts/it_consultant.txt
```
Ты профессиональный IT-консультант с глубокими знаниями в области технологий.

Твоя роль:
- Консультации по IT-технологиям и архитектурным решениям
- Помощь в решении технических проблем
- Code review и рекомендации по best practices
- Объяснение сложных технических концепций

Отвечай профессионально, используй технические термины где уместно.
Предоставляй практические примеры кода. Ссылайся на документацию и best practices.
```

### TDD Отчет (заполняется при выполнении)

```markdown
## 🔴 RED Phase: [Дата]
- ✅ Созданы падающие тесты для Config (load prompt from file)
- ✅ Созданы падающие тесты для команды /role
- ✅ Все тесты падают как ожидалось

## 🟢 GREEN Phase: [Дата]
- ✅ Config обновлен (system_prompt_file, role_name, role_description)
- ✅ Добавлен model_post_init() для загрузки промпта
- ✅ Добавлен handle_role() в MessageHandler
- ✅ Все тесты проходят

## 🔵 REFACTOR Phase: [Дата]
- ✅ Созданы примеры промптов (4 файла)
- ✅ Улучшено форматирование ответа /role
- ✅ Добавлено логирование
- ✅ Тесты остались зелеными

## Результаты:
- Coverage: XX%
- Тесты: XX passed, 0 failed
- Линтер: ✓
```

---

## Iteration 8: Полная интеграция

**Цель:** Все компоненты работают вместе
**Тест:** E2E сценарии

### Задачи

- [ ] Интеграционные тесты (все компоненты)
- [ ] Тест: диалог с контекстом (несколько сообщений)
- [ ] Тест: использование Wikipedia в диалоге
- [ ] Тест: команда /reset очищает контекст
- [ ] Тест: команда /role отображает корректную роль
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
4. `/role` → отображается роль бота
5. `/reset` → контекст очищен
6. Ошибка API → пользователь видит сообщение об ошибке

---

## Iteration 9: Docker + финализация

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
- [ ] Все команды работают (`/start`, `/help`, `/role`, `/reset`)
- [ ] Команда `/role` корректно отображает роль бота
- [ ] LLM отвечает на вопросы в соответствии с ролью
- [ ] Wikipedia tool работает
- [ ] Контекст сохраняется
- [ ] Системный промпт загружается из файла
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

- [vision.md](../vision.md) - техническое видение (v2.0 - ИИ-продукт с ролью)
- [idea.md](../idea.md) - концепция проекта (v2.0 - ИИ-продукт с ролью)
- [conventions.md](../conventions.md) - правила разработки
- **[.cursor/rules/qa_conventions.mdc](../../.cursor/rules/qa_conventions.mdc)** - TDD и тестирование
- **[.cursor/rules/workflow_tdd.mdc](../../.cursor/rules/workflow_tdd.mdc)** - TDD workflow (RED-GREEN-REFACTOR)

---

**Версия**: 2.0 (TDD + Role Management)
**Дата создания**: 10 октября 2025
**Последнее обновление**: 11 октября 2025
**Статус**: 🔲 TODO - готово к TDD разработке

