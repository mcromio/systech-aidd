# 🧪 Testing Guide - Руководство по тестированию

> Как писать и запускать тесты

---

## 🎯 Философия тестирования

**Зачем тесты:**
- Уверенность что код работает
- Документация поведения
- Безопасный рефакторинг
- Раннее обнаружение багов

**Подход:** Test-Driven Development (TDD)

---

## 📊 Текущее состояние

```
Tests:    55 passed, 0 failed
Coverage: 78%
Target:   85%+
```

---

## 🏗️ Структура тестов

```
tests/
├── __init__.py
├── test_config.py              # Config (Pydantic)
├── test_context_manager.py     # ContextManager
├── test_handlers.py            # MessageHandler
├── test_llm_client.py          # LLMClient
├── test_bot.py                 # TelegramBot
├── test_main.py                # main()
├── test_wikipedia_tool.py      # WikipediaTool
├── test_datetime_tool.py       # DateTimeTool
└── test_websearch_tool.py      # WebSearchTool
```

**Принцип:** 1 модуль src/ = 1 тестовый файл tests/

---

## 🔧 Инструменты

### pytest
```bash
# Запустить все тесты
pytest

# Запустить конкретный файл
pytest tests/test_config.py

# Запустить конкретный тест
pytest tests/test_config.py::test_config_loads_from_env

# Verbose режим
pytest -v
```

### pytest-asyncio
```python
# Для async тестов
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == "expected"
```

### pytest-cov
```bash
# Coverage отчет
pytest --cov=src

# С пропущенными строками
pytest --cov=src --cov-report=term-missing

# HTML отчет
pytest --cov=src --cov-report=html
# Откроется в htmlcov/index.html
```

---

## 📝 Написание тестов

### Unit Test - изолированный компонент

```python
# tests/test_context_manager.py
import pytest
from src.context_manager import ContextManager, UserContext
from src.config import Config

@pytest.fixture
def config():
    """Fixture для Config."""
    return Config(
        telegram_bot_token="test",
        openai_api_key="test",
        openai_proxy_url="http://test",
        max_context_messages=10
    )

@pytest.fixture
def context_manager(config):
    """Fixture для ContextManager."""
    return ContextManager(config)

def test_add_message(context_manager):
    """Тест добавления сообщения."""
    # Arrange
    user_id = 123

    # Act
    context_manager.add_message(user_id, "user", "Hello")

    # Assert
    history = context_manager.get_history(user_id)
    assert len(history) == 1
    assert history[0].role == "user"
    assert history[0].content == "Hello"

def test_clear_history(context_manager):
    """Тест очистки истории."""
    # Arrange
    user_id = 123
    context_manager.add_message(user_id, "user", "Hello")

    # Act
    context_manager.clear_history(user_id)

    # Assert
    history = context_manager.get_history(user_id)
    assert len(history) == 0
```

---

### Async Test

```python
# tests/test_wikipedia_tool.py
import pytest
from src.tools.wikipedia import WikipediaTool
from src.config import Config

@pytest.fixture
def config():
    return Config(
        telegram_bot_token="test",
        openai_api_key="test",
        openai_proxy_url="http://test"
    )

@pytest.fixture
def wiki_tool(config):
    return WikipediaTool(config)

@pytest.mark.asyncio
async def test_wikipedia_search(wiki_tool):
    """Тест поиска в Wikipedia."""
    # Act
    result = await wiki_tool.search("Python programming", "en")

    # Assert
    assert "Python" in result
    assert len(result) > 0
    assert "🔗 Источник:" in result
```

---

### Test с моками

```python
# tests/test_llm_client.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.llm_client import LLMClient
from src.config import Config
from src.context_manager import Message

@pytest.fixture
def config():
    return Config(
        telegram_bot_token="test",
        openai_api_key="test",
        openai_proxy_url="http://test",
        openai_model="gpt-4o-mini",
        system_prompt="Test prompt"
    )

@pytest.fixture
def llm_client(config):
    return LLMClient(config)

@pytest.mark.asyncio
async def test_get_response_simple(llm_client):
    """Тест получения ответа без tool calls."""
    # Arrange - создать mock response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Test response",
                tool_calls=None
            )
        )
    ]

    # Inject mock
    llm_client.openai_client.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    # Act
    messages = [Message(role="user", content="Hello")]
    response = await llm_client.get_response(messages)

    # Assert
    assert response == "Test response"
```

---

### Test с parametrize

```python
@pytest.mark.parametrize("user_id,expected_count", [
    (123, 1),
    (456, 1),
    (789, 1),
])
def test_add_message_multiple_users(context_manager, user_id, expected_count):
    """Тест добавления для разных пользователей."""
    context_manager.add_message(user_id, "user", "Hello")
    history = context_manager.get_history(user_id)
    assert len(history) == expected_count
```

---

## 🎭 Моки и Fixtures

### Когда использовать моки

**Мокать:**
- ✅ Внешние API (OpenAI, Wikipedia, DuckDuckGo)
- ✅ Сетевые запросы
- ✅ Файловая система (иногда)
- ✅ Время (datetime.now)

**НЕ мокать:**
- ❌ Простые функции
- ❌ Pydantic модели
- ❌ Внутреннюю логику

---

### Mock OpenAI API

```python
from unittest.mock import AsyncMock, MagicMock

# Mock completion response
mock_response = MagicMock()
mock_response.choices = [
    MagicMock(
        message=MagicMock(
            content="Response text",
            tool_calls=None
        )
    )
]

client.chat.completions.create = AsyncMock(return_value=mock_response)
```

---

### Mock Wikipedia

```python
from unittest.mock import MagicMock

# Mock Wikipedia page
mock_page = MagicMock()
mock_page.exists.return_value = True
mock_page.summary = "Test summary"
mock_page.fullurl = "https://test.url"

# Inject через monkeypatch
monkeypatch.setattr(tool.wiki_ru, 'page', lambda q: mock_page)
```

---

### Fixtures для переиспользования

```python
# conftest.py (в корне tests/)
import pytest
from src.config import Config

@pytest.fixture
def test_config():
    """Общий Config для всех тестов."""
    return Config(
        telegram_bot_token="test_token",
        openai_api_key="test_key",
        openai_proxy_url="http://test",
        openai_model="gpt-4o-mini",
        system_prompt="Test prompt",
        max_context_messages=10,
        max_tool_iterations=5
    )
```

---

## 📈 Coverage

### Измерить coverage

```bash
make test
# Output:
# src/config.py                96%
# src/context_manager.py      100%
# src/handlers.py              93%
# ...
# TOTAL                        78%
```

---

### Цель coverage

**Обязательно покрыть:**
- ✅ Бизнес-логика (handlers, context_manager)
- ✅ LLM интеграция (llm_client, orchestrator)
- ✅ Tools (wikipedia, datetime, websearch)

**Можно не покрывать:**
- ⚠️ main.py (точка входа)
- ⚠️ bot.py (интеграционный код)
- ⚠️ Config.__init__ (Pydantic)

**Target:** 85%+

---

### Найти непокрытые строки

```bash
pytest --cov=src --cov-report=term-missing

# Output:
# src/bot.py    28    28    0%   23-50, 55-65
#                                ↑ эти строки не покрыты
```

---

## 🚀 Запуск тестов

### Все тесты

```bash
make test
# или
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

### Только быстрые тесты

```bash
make test-quick
# или
pytest tests/ -v
```

---

### Конкретный файл

```bash
pytest tests/test_context_manager.py -v
```

---

### Конкретный тест

```bash
pytest tests/test_context_manager.py::test_add_message -v
```

---

### С detailed output

```bash
pytest tests/ -vv -s
# -vv: очень verbose
# -s: показывать print() в тестах
```

---

## 🔍 Debugging тестов

### Print отладка

```python
def test_something():
    result = compute()
    print(f"DEBUG: result = {result}")  # Увидим при pytest -s
    assert result == "expected"
```

```bash
pytest tests/test_something.py -s
# Output:
# DEBUG: result = actual_value
```

---

### Breakpoint

```python
def test_something():
    result = compute()
    import pdb; pdb.set_trace()  # Остановка здесь
    assert result == "expected"
```

```bash
pytest tests/test_something.py
# Откроется pdb debugger
```

---

## ✅ Best Practices

### Naming

```python
# ✅ Хорошие имена
def test_add_message_creates_new_context()
def test_get_response_with_tool_calls()
def test_config_validates_max_context_messages()

# ❌ Плохие имена
def test_1()
def test_feature()
```

---

### AAA Pattern (Arrange-Act-Assert)

```python
def test_something():
    # Arrange - подготовка
    manager = ContextManager(config)
    user_id = 123

    # Act - действие
    manager.add_message(user_id, "user", "Hello")

    # Assert - проверка
    history = manager.get_history(user_id)
    assert len(history) == 1
```

---

### Один assert на тест

```python
# ✅ Предпочтительно
def test_message_has_correct_role():
    msg = Message(role="user", content="test")
    assert msg.role == "user"

def test_message_has_correct_content():
    msg = Message(role="user", content="test")
    assert msg.content == "test"

# ⚠️ Допустимо но не идеально
def test_message_creation():
    msg = Message(role="user", content="test")
    assert msg.role == "user"
    assert msg.content == "test"
```

---

## 📚 Примеры для каждого типа

### Config Test

```python
def test_config_loads_from_kwargs():
    config = Config(
        telegram_bot_token="test",
        openai_api_key="test",
        openai_proxy_url="http://test"
    )
    assert config.telegram_bot_token == "test"
```

---

### Handler Test

```python
@pytest.mark.asyncio
async def test_handle_start(handler, mocker):
    # Mock message
    mock_msg = mocker.MagicMock()
    mock_msg.answer = AsyncMock()

    # Act
    await handler.handle_start(mock_msg)

    # Assert
    mock_msg.answer.assert_called_once()
```

---

### Tool Test

```python
@pytest.mark.asyncio
async def test_datetime_tool_returns_current_time(datetime_tool):
    result = await datetime_tool.execute(
        timezone="Europe/Moscow",
        format="full"
    )
    assert "🕐 Источник:" in result
    assert len(result) > 0
```

---

## 🎯 Чек-лист перед коммитом

- [ ] Все тесты проходят (`make test`)
- [ ] Coverage не упал
- [ ] Новый функционал покрыт тестами
- [ ] Тесты быстрые (< 5 сек все вместе)
- [ ] Моки для внешних API
- [ ] Понятные имена тестов
- [ ] AAA pattern соблюден

---

## 📚 Дополнительно

**Development Workflow:** [07_development_workflow.md](07_development_workflow.md)
**Conventions:** [../conventions.md](../conventions.md)
**Vision (тесты):** [../vision.md](../vision.md)


