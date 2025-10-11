# Code Conventions

> Правила разработки для LLM-ассистента Telegram бота  
> Полное техническое видение: [vision.md](vision.md)

---

## Основные принципы

### KISS (Keep It Simple, Stupid)
- Минимум абстракций
- Прямолинейная логика без оверинжиниринга
- Только необходимый функционал

### ООП структура
- **1 класс = 1 файл = 1 ответственность**
- Понятные имена классов и методов
- Композиция > наследование

---

## Структура кода

### Модули
```
src/
├── main.py              # Точка входа
├── config.py            # Config (Pydantic)
├── bot.py               # TelegramBot
├── handlers.py          # MessageHandler
├── llm_client.py        # LLMClient + function calling
├── context_manager.py   # ContextManager
└── wikipedia_tool.py    # WikipediaTool
```

### Архитектура
- **Config** → создается в main.py, передается через конструкторы
- **Dependency Injection** → явная передача зависимостей
- **Stateless** → минимум состояния, контекст in-memory dict
- **Async/await** → полностью асинхронный код

---

## Требования к коду

### Type Hints
```python
# ✅ Правильно
async def get_response(self, messages: list[Message]) -> str | None:
    pass

# ❌ Неправильно
async def get_response(self, messages):
    pass
```

### Docstrings
```python
# ✅ Правильно (на русском)
async def add_message(self, user_id: int, role: str, content: str) -> None:
    """Добавить сообщение в историю пользователя."""
    pass

# ❌ Неправильно (без docstring)
async def add_message(self, user_id: int, role: str, content: str) -> None:
    pass
```

### Pydantic модели
```python
# ✅ Всегда используй Pydantic для структур данных
from pydantic import BaseModel

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

# ❌ Не используй простые dict
message = {"role": "user", "content": "text"}
```

### Логирование
```python
import logging

logger = logging.getLogger(__name__)

# ✅ Логируй важные события
logger.info(f"Сообщение от пользователя {user_id}")
logger.error(f"Ошибка при обращении к LLM: {e}", exc_info=True)

# ❌ Не используй print()
print("Something happened")
```

---

## Обработка ошибок

### Try/Except
```python
# ✅ Явная обработка ошибок
try:
    response = await self.client.chat.completions.create(...)
    return response.choices[0].message.content
except Exception as e:
    logger.error(f"Ошибка: {e}", exc_info=True)
    return None

# ❌ Не игнорируй ошибки
response = await self.client.chat.completions.create(...)
return response.choices[0].message.content
```

---

## Зависимости

### Стек (см. [vision.md](vision.md#1-технологии))
- Python 3.12
- uv (управление зависимостями)
- aiogram 3.x (infinite_polling)
- openai (AsyncOpenAI)
- pydantic + pydantic-settings
- wikipedia-api
- pytest + ruff

---

## Тестирование

### Структура тестов
```python
# tests/test_context_manager.py
import pytest
from src.context_manager import ContextManager, Message

def test_add_message():
    """Тест добавления сообщения в историю."""
    # Arrange
    manager = ContextManager(config)
    
    # Act
    manager.add_message(123, "user", "Hello")
    
    # Assert
    assert len(manager.get_history(123)) == 1
```

### Требования
- Юнит-тесты для всех классов
- Моки для внешних API (OpenAI, Wikipedia)
- Coverage > 70%
- pytest + pytest-asyncio для async тестов

---

## Конфигурация

### .env файл
```bash
TELEGRAM_BOT_TOKEN=...
OPENAI_API_KEY=...
OPENAI_PROXY_URL=...  # прокси URL
OPENAI_MODEL=gpt-4o-mini
SYSTEM_PROMPT=You are a helpful assistant...
MAX_CONTEXT_MESSAGES=10
LOG_LEVEL=INFO
```

### Config класс
```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    telegram_bot_token: str
    openai_api_key: str
    openai_proxy_url: str  # прокси
    # ... см. vision.md раздел 5
```

---

## Важные паттерны

### Инициализация зависимостей (main.py)
```python
def main():
    # 1. Загрузка конфигурации
    config = Config()
    config.validate_config()
    
    # 2. Настройка логирования
    setup_logging(config.log_level)
    
    # 3. Создание компонентов
    context_manager = ContextManager(config)
    wikipedia_tool = WikipediaTool()
    llm_client = LLMClient(config, wikipedia_tool)
    message_handler = MessageHandler(config, context_manager, llm_client)
    
    # 4. Запуск бота
    bot = TelegramBot(config, message_handler)
    bot.start()
```

### Function Calling (LLMClient)
```python
# Схема инструментов
tools = [{
    "type": "function",
    "function": {
        "name": "search_wikipedia",
        "description": "Поиск информации в Wikipedia...",
        "parameters": {...}
    }
}]

# Цикл обработки tool calls (до 5 итераций)
for _ in range(5):
    response = await self.client.chat.completions.create(
        model=self.config.openai_model,
        messages=request_messages,
        tools=self.tools
    )
    
    if not response.choices[0].message.tool_calls:
        return response.choices[0].message.content
    
    # Выполнить tool calls и продолжить
    ...
```

---

## Что НЕ делать

❌ **Не создавай лишние абстракции** - нет базовых классов, интерфейсов без необходимости  
❌ **Не используй сложные паттерны** - нет фабрик, билдеров, стратегий для MVP  
❌ **Не дублируй код** - если логика повторяется > 2 раз, вынеси в метод  
❌ **Не используй print()** - только logging  
❌ **Не игнорируй типы** - type hints обязательны везде  
❌ **Не пиши длинные методы** - макс 30-40 строк, иначе разбивай  

---

## Чеклист для каждого файла

Перед отправкой кода проверь:

- [ ] Type hints для всех аргументов и возвращаемых значений
- [ ] Docstrings на русском для публичных методов
- [ ] Логирование важных событий и ошибок
- [ ] Try/except для внешних вызовов (API, файлы)
- [ ] Pydantic модели для всех структур данных
- [ ] Юнит-тесты для критичной логики
- [ ] Код соответствует ruff (линтер)
- [ ] Класс решает одну задачу (Single Responsibility)

---

## Полезные ссылки

- [vision.md](vision.md) - полное техническое видение проекта
- [idea.md](idea.md) - концепция проекта
- [README.md](../README.md) - инструкция по установке и использованию

---

**Версия**: 1.0  
**Дата**: 10 октября 2025  
**Принцип**: KISS - Keep It Simple, Stupid

