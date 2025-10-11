# Task List - Technical Debt & Code Quality

> Рефакторинг и улучшение качества кода после code review  
> Senior Tech Lead recommendations  
> Принцип: каждая итерация = работающий код + тесты + соответствие стандартам

---

## 📊 Отчет о прогрессе

| Итерация | Описание | Статус | Тесты | Дата |
|----------|----------|--------|-------|------|
| **TechDebt-1** | Исправление падающих тестов | ✅ DONE | ✅ | 2025-10-11 |
| **TechDebt-2** | Добавление mypy + type checking | 🔲 TODO | 🔲 | - |
| **TechDebt-3** | Устранение magic numbers (DRY) | 🔲 TODO | 🔲 | - |
| **TechDebt-4** | Рефакторинг Tools → Protocol | 🔲 TODO | 🔲 | - |
| **TechDebt-5** | Разделение LLMClient (SOLID) | 🔲 TODO | 🔲 | - |
| **TechDebt-6** | Повышение coverage до 85%+ | 🔲 TODO | 🔲 | - |

### Легенда статусов
- 🔲 TODO - не начато
- 🔄 IN PROGRESS - в работе
- ✅ DONE - завершено
- ❌ BLOCKED - заблокировано

---

## TechDebt-1: Исправление падающих тестов

**Цель:** Восстановить работоспособность всех тестов после рефакторинга  
**Текущее состояние:** 7 failed, 48 passed  
**Целевое состояние:** 0 failed, 55 passed

### Проблемы

1. **test_config.py** (3 теста)
   - `.env` файл перезаписывает mock переменные окружения
   - Изменился дефолт модели: `gpt-4o-mini` → `gpt-5`
   - `Config.__init__` читает `.env` явно

2. **test_datetime_tool.py** (2 теста)
   - Добавили строку "🕐 Источник: ..." в вывод
   - Тесты ожидают старый формат без источников

3. **test_llm_client.py** (2 теста)
   - Убрали параметр `temperature` для gpt-5
   - Добавили `datetime_tool` и `websearch_tool` (теперь 3 tools вместо 1)

### Задачи

- [x] Обновить `tests/test_config.py`:
  - Использовать kwargs для обхода чтения `.env` в тестах
  - Исправить проверку валидации

- [x] Обновить `tests/test_datetime_tool.py`:
  - Проверять наличие "🕐 Источник:" в результатах
  - Обновить assertions под новый формат

- [x] Обновить `tests/test_llm_client.py`:
  - Удалить проверку `temperature`
  - Обновить проверку количества tools (3 вместо 1)
  - Обновить `max_tokens` → `max_completion_tokens`

- [x] Запустить `make test` - должно быть 55 passed ✅

### Критерий готовности

```bash
# Все тесты проходят
make test
# Output: 55 passed in X.XXs

# Coverage не упал
# TOTAL: >= 75%

# Линтер проходит
make lint
# Output: All checks passed!
```

### ✅ Проверка соответствия стандартам

- [x] **conventions.mdc**: Type hints везде ✓
- [x] **conventions.mdc**: Docstrings на русском ✓
- [x] **conventions.mdc**: Логирование через logging ✓
- [x] **conventions.mdc**: Методы < 40 строк ✓
- [x] **vision.md**: Используется pytest ✓
- [x] **vision.md**: Coverage > 70% (75%) ✓
- [x] **workflow.mdc**: Тесты написаны и проходят ✓

---

## TechDebt-2: Добавление mypy + type checking

**Цель:** Добавить статическую типизацию для ранней ловли ошибок  
**Текущее состояние:** Type hints есть, но не проверяются  
**Целевое состояние:** `mypy` проходит без ошибок

### Задачи

- [ ] Добавить `mypy` в dev-зависимости:
  ```toml
  # pyproject.toml
  [dependency-groups]
  dev = [
      "mypy>=1.11.0",
      ...
  ]
  ```

- [ ] Настроить `mypy`:
  ```toml
  # pyproject.toml
  [tool.mypy]
  python_version = "3.12"
  strict = false  # Начать с false, потом включить
  warn_return_any = true
  warn_unused_configs = true
  disallow_untyped_defs = true
  disallow_any_generics = false
  
  [[tool.mypy.overrides]]
  module = ["aiogram.*", "wikipediaapi.*", "duckduckgo_search.*"]
  ignore_missing_imports = true
  ```

- [ ] Добавить команду в `Makefile`:
  ```makefile
  type-check: ## Проверка типов с mypy
      @echo "$(GREEN)Проверка типов...$(NC)"
      uv run mypy src/
  ```

- [ ] Исправить ошибки типизации (если есть)

- [ ] Добавить в `make check`:
  ```makefile
  check: lint type-check test ## Полная проверка кода
  ```

### Критерий готовности

```bash
# mypy проходит
make type-check
# Output: Success: no issues found in X source files

# Включено в общую проверку
make check
# Output: lint ✓, type-check ✓, test ✓
```

### ✅ Проверка соответствия стандартам

- [ ] **conventions.mdc**: Type hints обязательны везде ✓
- [ ] **vision.md**: Качество кода - type hints везде ✓
- [ ] **vision.md**: Инструменты разработки расширены ✓
- [ ] **workflow.mdc**: make команды обновлены ✓

---

## TechDebt-3: Устранение magic numbers (DRY)

**Цель:** Вынести все хардкоды в Config для единообразия  
**Текущее состояние:** Magic numbers в `llm_client.py`  
**Целевое состояние:** Все константы в Config

### Проблемы DRY

```python
# src/llm_client.py - ПЛОХО
max_websearch = 2  # хардкод
max_completion_tokens=10000  # хардкод
for iteration in range(10):  # магическое число
```

### Задачи

- [ ] Добавить параметры в `src/config.py`:
  ```python
  class Config(BaseSettings):
      # LLM параметры
      max_tool_iterations: int = Field(
          default=10,
          ge=1,
          le=20,
          description="Максимум итераций tool calling"
      )
      max_websearch_calls: int = Field(
          default=2,
          ge=1,
          le=5,
          description="Максимум веб-запросов за диалог"
      )
      max_completion_tokens: int = Field(
          default=10000,
          ge=1000,
          le=100000,
          description="Максимум токенов в ответе"
      )
  ```

- [ ] Обновить `src/llm_client.py`:
  ```python
  # Использовать из config
  for iteration in range(self.config.max_tool_iterations):
      ...
  
  websearch_count = 0
  max_websearch = self.config.max_websearch_calls
  
  max_completion_tokens=self.config.max_completion_tokens
  ```

- [ ] Добавить переменные в `.env.example`:
  ```bash
  # LLM параметры (опционально)
  MAX_TOOL_ITERATIONS=10
  MAX_WEBSEARCH_CALLS=2
  MAX_COMPLETION_TOKENS=10000
  ```

- [ ] Обновить `tests/test_config.py`:
  - Добавить тесты для новых полей
  - Проверить валидацию диапазонов

- [ ] Обновить `tests/test_llm_client.py`:
  - Проверить использование config параметров

### Критерий готовности

```bash
# Поиск хардкодов
rg "range\(10\)" src/llm_client.py
# Output: (пусто)

rg "max_websearch = 2" src/llm_client.py
# Output: (пусто)

# Тесты проходят
make test
# Output: 55 passed

# Можно переопределить через .env
echo "MAX_WEBSEARCH_CALLS=3" >> .env
python -c "from src.config import Config; print(Config().max_websearch_calls)"
# Output: 3
```

### ✅ Проверка соответствия стандартам

- [ ] **conventions.mdc**: DRY принцип соблюден ✓
- [ ] **conventions.mdc**: Pydantic для конфигурации ✓
- [ ] **vision.md**: Конфигурация через .env ✓
- [ ] **vision.md**: Pydantic валидация ✓

---

## TechDebt-4: Рефакторинг Tools → Protocol

**Цель:** Устранить дублирование в tools, ввести единый интерфейс  
**Текущее состояние:** Каждый tool - отдельный класс без общего интерфейса  
**Целевое состояние:** Все tools реализуют Protocol

### Проблемы

```python
# llm_client.py - дублирование схем
def _get_tools_schema(self):
    tools = []
    if self.wikipedia_tool:
        tools.append({ ... 20 строк ... })
    if self.datetime_tool:
        tools.append({ ... 20 строк ... })
    if self.websearch_tool:
        tools.append({ ... 20 строк ... })
```

### Задачи

- [ ] Создать `src/tools/__init__.py`

- [ ] Создать `src/tools/base.py` с Protocol:
  ```python
  from typing import Protocol, runtime_checkable
  
  @runtime_checkable
  class Tool(Protocol):
      """Базовый протокол для всех инструментов."""
      
      def get_schema(self) -> dict:
          """Возвращает JSON схему для OpenAI function calling."""
          ...
      
      async def execute(self, **kwargs) -> str:
          """Выполняет инструмент с аргументами."""
          ...
  ```

- [ ] Обновить существующие tools:
  - `src/tools/wikipedia.py` (переименовать из `wikipedia_tool.py`)
  - `src/tools/datetime.py` (переименовать из `datetime_tool.py`)
  - `src/tools/websearch.py` (переименовать из `websearch_tool.py`)
  
  Каждый реализует:
  ```python
  class WikipediaTool:
      def get_schema(self) -> dict:
          return {
              "type": "function",
              "function": { ... }
          }
      
      async def execute(self, query: str, language: str = "ru") -> str:
          return await self.search(query, language)
  ```

- [ ] Упростить `src/llm_client.py`:
  ```python
  def __init__(self, config: Config, tools: list[Tool] | None = None):
      self.config = config
      self.tools = tools or self._get_default_tools()
  
  def _get_default_tools(self) -> list[Tool]:
      from src.tools.wikipedia import WikipediaTool
      from src.tools.datetime import DateTimeTool
      from src.tools.websearch import WebSearchTool
      return [WikipediaTool(), DateTimeTool(), WebSearchTool()]
  
  def _get_tools_schema(self) -> list[dict]:
      return [tool.get_schema() for tool in self.tools]
  
  async def _execute_tool(self, tool_name: str, arguments: dict) -> str:
      for tool in self.tools:
          schema = tool.get_schema()
          if schema["function"]["name"] == tool_name:
              return await tool.execute(**arguments)
      return f"Ошибка: инструмент '{tool_name}' не найден"
  ```

- [ ] Обновить `src/main.py`:
  ```python
  from src.tools import WikipediaTool, DateTimeTool, WebSearchTool
  
  tools = [WikipediaTool(), DateTimeTool(), WebSearchTool()]
  llm_client = LLMClient(config, tools=tools)
  ```

- [ ] Обновить все импорты

- [ ] Обновить тесты

### Критерий готовности

```bash
# Структура src/tools
ls -la src/tools/
# Output: __init__.py, base.py, wikipedia.py, datetime.py, websearch.py

# Тесты проходят
make test
# Output: 55 passed

# Линтер проходит
make lint
# Output: All checks passed!

# Можно легко добавить новый tool
python -c "
from src.tools.base import Tool
from src.tools import WikipediaTool
assert isinstance(WikipediaTool(), Tool)
print('✓ WikipediaTool implements Tool protocol')
"
```

### ✅ Проверка соответствия стандартам

- [ ] **conventions.mdc**: 1 класс = 1 файл ✓
- [ ] **conventions.mdc**: DRY принцип ✓
- [ ] **conventions.mdc**: Type hints везде ✓
- [ ] **vision.md**: ООП с четкой структурой ✓
- [ ] **vision.md**: Композиция > наследование ✓

---

## TechDebt-5: Разделение LLMClient (SOLID)

**Цель:** Разбить LLMClient на компоненты (Single Responsibility)  
**Текущее состояние:** LLMClient делает слишком много  
**Целевое состояние:** Разделены обязанности

### Проблемы SRP

```python
# LLMClient делает:
# 1. HTTP клиент конфигурация
# 2. OpenAI API вызовы
# 3. Tool orchestration (цикл function calling)
# 4. Логика ограничений (websearch_count)
```

### Задачи

- [ ] Создать `src/llm/__init__.py`

- [ ] Создать `src/llm/client.py` (чистый OpenAI wrapper):
  ```python
  class OpenAIClient:
      """Простой wrapper над OpenAI API."""
      
      def __init__(self, config: Config):
          http_client = httpx.AsyncClient(
              proxy=config.openai_proxy_url,
              timeout=config.openai_timeout,
          )
          self.client = AsyncOpenAI(
              api_key=config.openai_api_key,
              http_client=http_client,
          )
          self.config = config
      
      async def create_completion(
          self,
          messages: list[dict],
          tools: list[dict] | None = None,
      ) -> CompletionResponse:
          """Создать completion с tools."""
          ...
  ```

- [ ] Создать `src/llm/orchestrator.py` (tool calling loop):
  ```python
  class ToolOrchestrator:
      """Управление function calling циклом."""
      
      def __init__(
          self,
          openai_client: OpenAIClient,
          tools: list[Tool],
          config: Config,
      ):
          self.openai_client = openai_client
          self.tools = tools
          self.config = config
      
      async def process_with_tools(
          self,
          messages: list[Message],
      ) -> str | None:
          """Обработать запрос с tool calling."""
          # Цикл на max_tool_iterations
          # Логика websearch_count
          # Вызов tools
          ...
  ```

- [ ] Обновить `src/llm_client.py` (фасад для обратной совместимости):
  ```python
  class LLMClient:
      """Фасад для работы с LLM (обратная совместимость)."""
      
      def __init__(self, config: Config, tools: list[Tool] | None = None):
          self.openai_client = OpenAIClient(config)
          self.tools = tools or self._get_default_tools()
          self.orchestrator = ToolOrchestrator(
              self.openai_client,
              self.tools,
              config,
          )
      
      async def get_response(self, messages: list[Message]) -> str | None:
          return await self.orchestrator.process_with_tools(messages)
  ```

- [ ] Обновить тесты:
  - `tests/test_llm/test_client.py` - OpenAI wrapper
  - `tests/test_llm/test_orchestrator.py` - tool calling
  - `tests/test_llm_client.py` - фасад (обратная совместимость)

- [ ] Убедиться что все импорты работают

### Критерий готовности

```bash
# Структура src/llm
ls -la src/llm/
# Output: __init__.py, client.py, orchestrator.py

# Тесты проходят
make test
# Output: >= 55 passed (могут быть новые)

# Старый код работает (обратная совместимость)
python -c "
from src.llm_client import LLMClient
from src.config import Config
client = LLMClient(Config())
print('✓ LLMClient работает как фасад')
"

# Новый код тоже работает
python -c "
from src.llm.client import OpenAIClient
from src.llm.orchestrator import ToolOrchestrator
print('✓ Новая структура импортируется')
"
```

### ✅ Проверка соответствия стандартам

- [ ] **conventions.mdc**: 1 класс = 1 ответственность ✓
- [ ] **conventions.mdc**: 1 класс = 1 файл ✓
- [ ] **conventions.mdc**: Методы < 40 строк ✓
- [ ] **vision.md**: SOLID принципы ✓
- [ ] **vision.md**: Явность > неявность ✓
- [ ] **vision.md**: Композиция работает ✓

---

## TechDebt-6: Повышение coverage до 85%+

**Цель:** Увеличить покрытие тестами критичного кода  
**Текущее состояние:** 75% coverage  
**Целевое состояние:** 85%+ coverage

### Coverage gaps (текущие)

```
src/bot.py                28 строк    0%   ← КРИТИЧНО
src/main.py               31 строка   0%   ← КРИТИЧНО
src/llm_client.py         84 строки  80%   ← 17 строк непокрыто
src/websearch_tool.py     42 строки  86%   ← 6 строк непокрыто
```

### Задачи

- [ ] **Покрыть `src/bot.py` (приоритет HIGH)**:
  ```python
  # tests/test_bot.py
  @pytest.mark.asyncio
  async def test_telegram_bot_init():
      """Тест инициализации бота."""
      ...
  
  @pytest.mark.asyncio
  async def test_telegram_bot_register_handlers():
      """Тест регистрации handlers."""
      # Mock aiogram.Router
      ...
  ```

- [ ] **Покрыть `src/main.py` (приоритет HIGH)**:
  ```python
  # tests/test_main.py
  def test_setup_logging():
      """Тест настройки логирования."""
      ...
  
  @pytest.mark.asyncio
  async def test_main_integration():
      """Интеграционный тест main (с моками)."""
      # Mock aiogram, не запускать реально
      ...
  ```

- [ ] **Дополнить `tests/test_llm_client.py`**:
  - Покрыть error handling paths
  - Покрыть websearch_count логику полностью
  - Покрыть достижение лимита итераций

- [ ] **Дополнить `tests/test_websearch_tool.py`**:
  - Покрыть exception handling в DuckDuckGo
  - Покрыть случай пустых результатов

- [ ] **Добавить integration test**:
  ```python
  # tests/test_integration.py
  @pytest.mark.asyncio
  async def test_full_message_flow():
      """End-to-end тест всего пайплайна."""
      # User message → ContextManager → LLMClient → Tools → Response
      ...
  ```

- [ ] Настроить `pyproject.toml`:
  ```toml
  [tool.coverage.report]
  fail_under = 85
  exclude_lines = [
      "pragma: no cover",
      "def __repr__",
      "raise AssertionError",
      "raise NotImplementedError",
      "if __name__ == .__main__.:",
      "if TYPE_CHECKING:",
  ]
  ```

### Критерий готовности

```bash
# Coverage >= 85%
make test
# Output: TOTAL ... 85% (или выше)

# Покрыты критичные файлы
uv run pytest --cov=src --cov-report=term-missing
# bot.py > 80%
# main.py > 80%
# llm_client.py > 85%

# Все тесты проходят
# Output: >= 70 passed (добавили ~15 новых тестов)
```

### ✅ Проверка соответствия стандартам

- [ ] **conventions.mdc**: Юнит-тесты для критичной логики ✓
- [ ] **conventions.mdc**: Coverage > 70% (теперь 85%+) ✓
- [ ] **vision.md**: pytest для тестирования ✓
- [ ] **vision.md**: Качество кода подтверждено ✓
- [ ] **workflow.mdc**: Тесты проходят ✓

---

## 📝 Общие правила выполнения

### Перед началом каждой итерации

1. ✅ Прочитать описание итерации
2. ✅ Согласовать подход с пользователем
3. ✅ Обновить статус в таблице → 🔄 IN PROGRESS

### Во время итерации

1. ✅ Следовать всем соглашениям из `conventions.mdc`
2. ✅ Следовать принципам из `vision.md`
3. ✅ Писать docstrings на русском
4. ✅ Type hints везде
5. ✅ Методы < 40 строк
6. ✅ DRY принцип

### После завершения итерации

1. ✅ Запустить `make format`
2. ✅ Запустить `make lint` (должен пройти)
3. ✅ Запустить `make test` (все тесты проходят)
4. ✅ Запустить `make type-check` (с TechDebt-2)
5. ✅ Проверить все чекбоксы "✅ Проверка соответствия стандартам"
6. ✅ Показать результаты пользователю
7. ✅ Дождаться подтверждения
8. ✅ Обновить статус в таблице → ✅ DONE
9. ✅ Создать коммит

### Формат коммита

```bash
git add .
git commit -m "refactor(techdebt-N): Краткое описание

- Что сделано 1
- Что сделано 2
- Coverage: XX%
- Tests: XX passed

Refs: #techdebt-N"
```

---

## 🎯 Ожидаемый результат после всех итераций

### Метрики качества

| Метрика | Было | Стало |
|---------|------|-------|
| Тесты | 48 passed, 7 failed | 70+ passed, 0 failed |
| Coverage | 75% | 85%+ |
| Линтер | ruff ✓ | ruff + mypy ✓ |
| Magic numbers | Да | Нет (Config) |
| SRP нарушения | Да (LLMClient) | Нет |
| DRY нарушения | Да (tools) | Нет (Protocol) |

### Архитектура

**Было:**
```
src/
├── llm_client.py (300+ строк, делает всё)
├── wikipedia_tool.py
├── datetime_tool.py
└── websearch_tool.py
```

**Стало:**
```
src/
├── llm/
│   ├── client.py (OpenAI wrapper)
│   └── orchestrator.py (tool calling)
├── tools/
│   ├── base.py (Protocol)
│   ├── wikipedia.py
│   ├── datetime.py
│   └── websearch.py
└── llm_client.py (фасад для совместимости)
```

### Команды разработчика

```bash
make format      # Форматирование
make lint        # Ruff проверка
make type-check  # Mypy проверка типов ← NEW
make test        # Тесты с coverage
make check       # lint + type-check + test ← UPDATED
```

---

**Принцип:** KISS + SOLID + DRY = Качественный код  
**Версия:** 1.0  
**Дата создания:** 11 октября 2025

