# Техническое видение проекта LLM-ассистент

> Дата создания: 10 октября 2025  
> Версия: 1.0  
> Принцип: KISS - максимальная простота для MVP

---

## 1. Технологии

### Основной стек
- **Python 3.12** - основной язык разработки
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram 3.x** - фреймворк для Telegram Bot API (метод infinite_polling)
- **openai** - официальный клиент для работы с OpenAI API
- **make** - автоматизация команд разработки

### Дополнительные библиотеки
- **python-dotenv** - загрузка переменных окружения из .env файла
- **pydantic** - валидация конфигурации и структур данных
- **logging** - стандартная библиотека для логирования

### Инструменты разработки
- **ruff** - современный линтер и форматтер (замена black + flake8 + isort)
- **pytest** - фреймворк для юнит-тестирования
- **mypy** - статическая проверка типов (добавляется в TechDebt-2)
- **pytest-cov** - измерение покрытия тестами

---

## 2. Принципы разработки

### KISS (Keep It Simple, Stupid)
- Минимум абстракций и избыточных паттернов
- Прямолинейная логика без оверинжиниринга
- Только необходимый функционал для MVP

### ООП с четкой структурой
- **1 класс = 1 файл = 1 ответственность**
- Понятные имена классов и методов
- Композиция предпочтительнее наследования
- Минимум иерархий классов

### Явность (Explicit over Implicit)
- Явная передача зависимостей между классами
- Полные type hints для всех аргументов и возвращаемых значений
- Явная обработка ошибок (try/except где нужно)

### Stateless подход
- Контекст диалогов хранится in-memory (dict по user_id)
- Минимум состояния в классах
- Без БД в MVP (легко добавить позже при необходимости)

### Асинхронность
- Полностью async/await (требование aiogram)
- Все IO операции асинхронные

### Качество кода
- **Type hints** везде (обязательно для всех аргументов и возвратов, Python 3.12 стиль)
- **Docstrings** на русском для всех публичных методов
- **Логирование** только через logging (не print())
- **Короткие методы** максимум 30-40 строк
- **Юнит-тесты** для критичной бизнес-логики (coverage >= 85%)
- **SOLID принципы** - особенно Single Responsibility
- **DRY принцип** - не дублировать код > 2 раз
- **Magic numbers → Config** - все константы в конфигурации

---

## 3. Структура проекта

```
systech-aidd_mcr/
├── src/
│   ├── __init__.py
│   ├── main.py              # Точка входа, запуск бота
│   ├── bot.py               # TelegramBot класс (aiogram setup)
│   ├── handlers.py          # MessageHandler класс (обработка сообщений)
│   ├── llm_client.py        # LLMClient класс (фасад, обратная совместимость)
│   ├── context_manager.py   # ContextManager класс (история диалогов)
│   ├── config.py            # Config класс (настройки из .env)
│   │
│   ├── llm/                 # ← NEW (TechDebt-5): LLM компоненты
│   │   ├── __init__.py
│   │   ├── client.py        # OpenAIClient (чистый wrapper OpenAI API)
│   │   └── orchestrator.py  # ToolOrchestrator (tool calling loop)
│   │
│   └── tools/               # ← NEW (TechDebt-4): Tools с Protocol
│       ├── __init__.py
│       ├── base.py          # Tool Protocol (интерфейс)
│       ├── wikipedia.py     # WikipediaTool
│       ├── datetime.py      # DateTimeTool
│       └── websearch.py     # WebSearchTool
│
├── tests/
│   ├── __init__.py
│   ├── test_context_manager.py
│   ├── test_llm_client.py
│   ├── test_handlers.py
│   ├── test_llm/            # ← NEW: тесты для llm компонентов
│   │   ├── test_client.py
│   │   └── test_orchestrator.py
│   ├── test_tools/          # ← NEW: тесты для tools
│   │   └── ...
│   └── test_integration.py  # ← NEW: интеграционные тесты
│
├── docs/
│   ├── idea.md              # Концепция проекта
│   ├── vision.md            # Техническое видение (этот документ)
│   ├── tasklist.md          # Основной tasklist (MVP)
│   ├── tasklist_tech_dept.md # ← NEW: Tech debt roadmap
│   ├── workflow.md          # Workflow для основной разработки
│   └── workflow_tech_debt.md # ← NEW: Workflow для tech debt
│
├── .cursor/
│   └── rules/
│       ├── conventions.mdc  # Правила разработки (обновлены)
│       └── workflow.mdc     # Workflow правила
│
├── .env.example             # Шаблон переменных окружения
├── .env                     # Реальные токены (в .gitignore)
├── .gitignore
├── pyproject.toml           # Конфигурация проекта и зависимостей (uv)
├── Makefile                 # Команды для разработки
└── README.md                # Документация для пользователей
```

### Описание модулей

#### src/main.py
- Точка входа в приложение
- Инициализация всех компонентов
- Запуск бота через infinite_polling

#### src/bot.py
- Класс `TelegramBot`
- Настройка aiogram Bot и Dispatcher
- Регистрация handlers

#### src/handlers.py
- Класс `MessageHandler`
- Обработка команд: `/start`, `/help`, `/reset`
- Обработка текстовых сообщений

#### src/llm_client.py
- Класс `LLMClient`
- Обертка над OpenAI API client
- Формирование запросов с системным промптом

#### src/context_manager.py
- Класс `ContextManager`
- Хранение истории диалогов по user_id
- Ограничение размера истории

#### src/config.py
- Класс `Config` на основе Pydantic
- Загрузка и валидация настроек из .env
- Системный промпт и параметры LLM

---

## 4. Архитектура проекта

### Общая схема взаимодействия

```
User (Telegram)
    ↓
[TelegramBot] - настройка aiogram Bot + Dispatcher
    ↓
[MessageHandler] - обработка команд и сообщений
    ↓ ↑
    ↓ └─────────────┐
    ↓               ↓
[ContextManager]  [LLMClient] → OpenAI API (через прокси)
 (история)         ↓
    ↓              ↓
in-memory dict   ответ от LLM
    ↓              ↓
    └──────────────┘
         ↓
Response → User
```

### Компоненты и ответственность

#### 1. Config (config.py)
**Ответственность:** Загрузка и валидация конфигурации

**Поля:**
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `OPENAI_API_KEY` - ключ OpenAI API
- `OPENAI_PROXY_URL` - URL прокси для OpenAI API
- `OPENAI_MODEL` - название модели (gpt-4, gpt-3.5-turbo и т.д.)
- `SYSTEM_PROMPT` - системный промпт для LLM
- `MAX_CONTEXT_MESSAGES` - макс. количество сообщений в истории
- `LOG_LEVEL` - уровень логирования

**Технология:** Pydantic BaseSettings для автозагрузки из .env

#### 2. TelegramBot (bot.py)
**Ответственность:** Настройка и запуск Telegram бота

**Методы:**
- `__init__(config, message_handler)` - инициализация Bot и Dispatcher
- `register_handlers()` - регистрация handlers в диспетчере
- `start()` - запуск infinite_polling

**Зависимости:** Config, MessageHandler

#### 3. MessageHandler (handlers.py)
**Ответственность:** Обработка всех входящих команд и сообщений

**Методы:**
- `__init__(config, context_manager, llm_client)` - инициализация
- `handle_start(message)` - команда /start
- `handle_help(message)` - команда /help
- `handle_reset(message)` - команда /reset (очистка истории)
- `handle_message(message)` - обработка текстовых сообщений

**Логика обработки сообщения:**
1. Получить user_id из message
2. Добавить сообщение пользователя в контекст
3. Получить историю из ContextManager
4. Отправить историю в LLMClient
5. Получить ответ от LLM
6. Добавить ответ в контекст
7. Отправить ответ пользователю
8. При ошибке - отправить сообщение "Произошла ошибка, попробуйте позже"

**Зависимости:** Config, ContextManager, LLMClient

#### 4. ContextManager (context_manager.py)
**Ответственность:** Управление историей диалогов

**Структура данных:**
```python
contexts: dict[int, list[dict]] = {}
# user_id -> [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
```

**Методы:**
- `__init__(config)` - инициализация
- `add_message(user_id, role, content)` - добавить сообщение
- `get_history(user_id)` - получить историю (последние N сообщений)
- `clear_history(user_id)` - очистить историю пользователя
- `_trim_history(user_id)` - обрезать историю до MAX_CONTEXT_MESSAGES

**Зависимости:** Config

#### 5. LLMClient (llm_client.py)
**Ответственность:** Работа с OpenAI API

**Методы:**
- `__init__(config)` - инициализация AsyncOpenAI с прокси
- `get_response(messages)` - получить ответ от LLM

**Формирование запроса:**
```python
request_messages = [
    {"role": "system", "content": config.system_prompt},
    *messages  # история диалога
]
```

**Обработка ошибок:**
- Try/except для всех вызовов OpenAI API
- Логирование ошибок
- Возврат None при ошибке

**Зависимости:** Config

### Поток данных

#### Сценарий 1: Пользователь отправляет сообщение
1. User отправляет текст в Telegram
2. TelegramBot получает Update через aiogram
3. MessageHandler.handle_message() вызывается
4. ContextManager добавляет сообщение пользователя
5. ContextManager возвращает историю диалога
6. LLMClient отправляет запрос в OpenAI (через прокси)
7. LLMClient возвращает ответ
8. ContextManager добавляет ответ ассистента
9. MessageHandler отправляет ответ пользователю в Telegram

#### Сценарий 2: Команда /reset
1. User отправляет /reset
2. MessageHandler.handle_reset() вызывается
3. ContextManager.clear_history(user_id)
4. MessageHandler отправляет подтверждение

### Принципы архитектуры

1. **Dependency Injection**
   - Config создается в main.py
   - Передается через конструкторы всем компонентам
   - Явные зависимости

2. **Слабая связанность**
   - Каждый компонент независим
   - Зависимости только через интерфейсы (type hints)

3. **Единая ответственность**
   - Каждый класс решает одну задачу
   - 1 класс = 1 файл

4. **Простота**
   - Нет абстрактных классов и интерфейсов
   - Нет сложных паттернов (фабрики, билдеры и т.д.)
   - Прямолинейная логика

---

## 5. Модель данных

### Pydantic модели

Все структуры данных описаны через Pydantic для валидации и типобезопасности.

#### 1. Config (config.py)

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """Конфигурация приложения."""
    
    telegram_bot_token: str
    openai_api_key: str
    openai_proxy_url: str
    openai_timeout: float = 30.0
    openai_model: str = "gpt-4o-mini"
    system_prompt: str = "Ты полезный ассистент. Отвечай на вопросы пользователя."
    max_context_messages: int = 10
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

#### 2. Message (context_manager.py)

```python
from pydantic import BaseModel

class Message(BaseModel):
    """Сообщение в диалоге."""
    
    role: Literal["user", "assistant", "system"]
    content: str
```

#### 3. UserContext (context_manager.py)

```python
from pydantic import BaseModel

class UserContext(BaseModel):
    """Контекст диалога пользователя."""
    
    user_id: int
    messages: list[Message] = []
    
    def add_message(self, role: str, content: str) -> None:
        """Добавить сообщение в историю."""
        self.messages.append(Message(role=role, content=content))
    
    def get_messages(self, limit: int) -> list[Message]:
        """Получить последние N сообщений."""
        return self.messages[-limit:] if limit > 0 else self.messages
    
    def clear(self) -> None:
        """Очистить историю."""
        self.messages = []
```

### Структура хранения данных

#### In-memory хранилище (ContextManager)

```python
contexts: dict[int, UserContext] = {}
# user_id (Telegram ID) -> UserContext
```

**Операции:**
- Создание контекста при первом сообщении
- Добавление сообщений в историю
- Получение истории с ограничением
- Очистка истории по команде

**Ограничения:**
- История теряется при перезапуске бота (для MVP приемлемо)
- Нет персистентности (легко добавить SQLite позже)
- Память растет с количеством пользователей (для MVP не критично)

### Формат данных для OpenAI API

```python
# Запрос к OpenAI
request_messages = [
    {"role": "system", "content": config.system_prompt},
    {"role": "user", "content": "Привет!"},
    {"role": "assistant", "content": "Здравствуйте! Чем могу помочь?"},
    {"role": "user", "content": "Как дела?"}
]

# Ответ от OpenAI
response = {
    "id": "chatcmpl-xxx",
    "object": "chat.completion",
    "choices": [{
        "message": {
            "role": "assistant",
            "content": "У меня всё хорошо, спасибо!"
        }
    }]
}
```

### Константы и дефолтные значения

```python
# Дефолтные значения
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_CONTEXT = 10
DEFAULT_SYSTEM_PROMPT = "Ты полезный ассистент. Отвечай на вопросы пользователя вежливо и информативно."
DEFAULT_LOG_LEVEL = "INFO"

# Лимиты
MAX_MESSAGE_LENGTH = 4096  # Лимит Telegram
MAX_CONTEXT_MESSAGES = 50  # Жесткий лимит
```

### Примеры данных

#### Пример UserContext

```python
UserContext(
    user_id=123456789,
    messages=[
        Message(role="user", content="Привет!"),
        Message(role="assistant", content="Здравствуйте!"),
        Message(role="user", content="Как погода?"),
        Message(role="assistant", content="Я не имею доступа к текущим данным о погоде.")
    ]
)
```

#### Пример Config из .env

```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_PROXY_URL=https://api.your-proxy.com/v1
OPENAI_TIMEOUT=30.0
OPENAI_MODEL=gpt-4o-mini
SYSTEM_PROMPT=Ты эксперт в программировании на Python. Помогай с кодом.
MAX_CONTEXT_MESSAGES=15
LOG_LEVEL=DEBUG
```

---

## 6. Работа с LLM

### Общий подход

Работа с LLM организована через класс `LLMClient`, который:
1. Инициализирует OpenAI клиент с прокси
2. Формирует запросы с системным промптом и историей
3. Обрабатывает function calling (инструменты)
4. Обрабатывает ошибки и логирует их

### LLMClient (llm_client.py)

#### Инициализация

```python
from openai import AsyncOpenAI

class LLMClient:
    def __init__(self, config: Config, wikipedia_tool: WikipediaTool):
        """Инициализация LLM клиента."""
        self.config = config
        self.wikipedia_tool = wikipedia_tool
        
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            http_client=httpx.AsyncClient(
                proxy=config.openai_proxy_url,
                timeout=config.openai_timeout
            )
        )
        
        self.tools = self._get_tools_schema()
```

#### Основной метод get_response

```python
async def get_response(self, messages: list[Message]) -> str | None:
    """
    Получить ответ от LLM.
    
    Обрабатывает function calling автоматически в цикле.
    """
    try:
        # Формируем запрос
        request_messages = [
            {"role": "system", "content": self.config.system_prompt},
            *[msg.model_dump() for msg in messages]
        ]
        
        # Основной цикл обработки (может быть несколько tool calls)
        max_iterations = 5
        for _ in range(max_iterations):
            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=request_messages,
                tools=self.tools,
                temperature=0.7,
                max_tokens=2000
            )
            
            message = response.choices[0].message
            
            # Если нет tool calls - возвращаем ответ
            if not message.tool_calls:
                return message.content
            
            # Обрабатываем tool calls
            request_messages.append(message)
            
            for tool_call in message.tool_calls:
                tool_response = await self._execute_tool(tool_call)
                request_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_response
                })
        
        return "Превышен лимит итераций обработки запроса."
        
    except Exception as e:
        logger.error(f"Ошибка при обращении к LLM: {e}")
        return None
```

#### Выполнение tools

```python
async def _execute_tool(self, tool_call) -> str:
    """Выполнить вызов инструмента."""
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    if function_name == "search_wikipedia":
        return await self.wikipedia_tool.search(
            query=arguments["query"],
            language=arguments.get("language", "ru")
        )
    
    return "Неизвестный инструмент"
```

#### Схема tools

```python
def _get_tools_schema(self) -> list[dict]:
    """Получить схему доступных инструментов."""
    return [
        {
            "type": "function",
            "function": {
                "name": "search_wikipedia",
                "description": "Поиск информации в Wikipedia. Используй этот инструмент, когда нужны фактические данные, определения, исторические факты.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Поисковый запрос для Wikipedia"
                        },
                        "language": {
                            "type": "string",
                            "enum": ["ru", "en"],
                            "description": "Язык Wikipedia (по умолчанию ru)"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
```

### WikipediaTool (wikipedia_tool.py)

```python
import wikipediaapi
from typing import Optional

class WikipediaTool:
    """Инструмент для поиска информации в Wikipedia."""
    
    def __init__(self, user_agent: str = "LLM-Assistant-Bot/1.0"):
        """Инициализация Wikipedia клиента."""
        self.wiki_ru = wikipediaapi.Wikipedia(
            language='ru',
            user_agent=user_agent
        )
        self.wiki_en = wikipediaapi.Wikipedia(
            language='en',
            user_agent=user_agent
        )
    
    async def search(self, query: str, language: str = "ru") -> str:
        """
        Поиск статьи в Wikipedia.
        
        Args:
            query: Поисковый запрос
            language: Язык (ru/en)
            
        Returns:
            Краткое содержание статьи или сообщение об ошибке
        """
        try:
            wiki = self.wiki_ru if language == "ru" else self.wiki_en
            page = wiki.page(query)
            
            if not page.exists():
                return f"Статья '{query}' не найдена в Wikipedia ({language})."
            
            # Возвращаем summary (первый абзац), макс 500 символов
            summary = page.summary[:500]
            
            if len(page.summary) > 500:
                summary += "..."
            
            return f"{summary}\n\nИсточник: {page.fullurl}"
            
        except Exception as e:
            logger.error(f"Ошибка поиска в Wikipedia: {e}")
            return f"Ошибка при поиске в Wikipedia: {str(e)}"
```

### Параметры LLM

Параметры запросов к OpenAI:
- **model**: из конфига (`gpt-4o-mini` по умолчанию)
- **temperature**: `0.7` (баланс креативности и точности)
- **max_tokens**: `2000` (достаточно для развернутых ответов)
- **tools**: список доступных инструментов

### Обработка ошибок

Типы ошибок и их обработка:

1. **OpenAI API ошибки**
   - Timeout - логируем, возвращаем None
   - Rate limit - логируем, возвращаем None
   - Invalid API key - логируем, возвращаем None
   - Network errors - логируем, возвращаем None

2. **Wikipedia ошибки**
   - Статья не найдена - возвращаем сообщение
   - Network errors - возвращаем сообщение об ошибке

3. **Function calling ошибки**
   - Превышен лимит итераций (5) - возвращаем сообщение
   - Некорректные аргументы - логируем, возвращаем ошибку

### Поток работы с tools

```
User: "Кто такой Пушкин?"
    ↓
LLMClient формирует запрос с tools
    ↓
OpenAI решает использовать search_wikipedia
    ↓
LLMClient вызывает WikipediaTool.search("Пушкин", "ru")
    ↓
WikipediaTool возвращает summary из Wikipedia
    ↓
LLMClient отправляет результат обратно в OpenAI
    ↓
OpenAI формирует итоговый ответ пользователю
    ↓
User получает: "Александр Сергеевич Пушкин (1799-1837) - русский поэт..."
```

### Расширяемость

Для добавления новых инструментов:
1. Создать новый класс Tool (например, `WeatherTool`)
2. Добавить схему в `_get_tools_schema()`
3. Добавить обработку в `_execute_tool()`
4. Передать экземпляр в `LLMClient.__init__()`

Принцип: один инструмент = один класс = один файл.

### Обновление структуры проекта

Добавляется файл:
```
src/
├── wikipedia_tool.py    # WikipediaTool класс
└── ...
```

### Обновление зависимостей

В `pyproject.toml` добавляются:
```toml
dependencies = [
    "aiogram>=3.0.0",
    "openai>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "wikipedia-api>=0.6.0",
]
```

---

## 7. Сценарии работы

### Сценарий 1: Первый запуск бота

```
User: /start
Bot:  Привет! Я LLM-ассистент с доступом к Wikipedia.
      
      Задавайте мне вопросы, и я постараюсь помочь!
      
      Доступные команды:
      /help - показать справку
      /reset - очистить историю диалога
```

### Сценарий 2: Обычный диалог без инструментов

```
User: Привет! Как дела?
Bot:  Здравствуйте! У меня всё отлично, спасибо. Чем могу помочь?

User: Напиши функцию на Python для сортировки списка
Bot:  Конечно! Вот простая функция для сортировки:
      
      def sort_list(items: list) -> list:
          """Сортировка списка."""
          return sorted(items)
      
      Использование: result = sort_list([3, 1, 2])
```

### Сценарий 3: Диалог с использованием Wikipedia

```
User: Кто такой Александр Пушкин?
Bot:  [LLM решает использовать Wikipedia tool]
      
      Александр Сергеевич Пушкин (1799-1837) — русский поэт, драматург 
      и прозаик, заложивший основы русского реалистического направления, 
      критик и теоретик литературы, историк, публицист...
      
      Источник: https://ru.wikipedia.org/wiki/Пушкин

User: В каком году он родился?
Bot:  [Использует контекст предыдущего ответа]
      
      Александр Пушкин родился в 1799 году.
```

### Сценарий 4: Сброс контекста диалога

```
User: /reset
Bot:  ✅ История диалога очищена. Начнем сначала!

User: Привет
Bot:  [Отвечает без контекста предыдущих сообщений]
      Здравствуйте! Чем могу помочь?
```

### Сценарий 5: Команда помощи

```
User: /help
Bot:  📖 Справка по боту
      
      Я — LLM-ассистент на базе GPT модели с доступом к Wikipedia.
      
      Возможности:
      • Отвечаю на вопросы
      • Помогаю с кодом
      • Ищу информацию в Wikipedia
      • Помню контекст диалога
      
      Команды:
      /start - начать работу
      /help - эта справка
      /reset - очистить историю
```

### Сценарий 6: Ошибка OpenAI API

```
User: Расскажи про квантовую физику
Bot:  [OpenAI API недоступен]
      
      ❌ Произошла ошибка при обработке запроса. Попробуйте позже.

[В логах]:
ERROR: Ошибка при обращении к LLM: Connection timeout
```

### Сценарий 7: Ошибка Wikipedia

```
User: Расскажи про несуществующую_статью_12345
Bot:  [Wikipedia не нашла статью]
      
      Я попытался найти информацию в Wikipedia, но статья 
      'несуществующую_статью_12345' не найдена. 
      
      Могу ли помочь чем-то еще?
```

### Сценарий 8: Длинный диалог (превышение лимита контекста)

```
[После 10+ сообщений в диалоге]

User: Что я спрашивал в самом начале?
Bot:  [ContextManager хранит только последние N сообщений]
      
      К сожалению, я помню только последние 10 сообщений нашего диалога.
      Используйте /reset чтобы начать новый разговор.
```

### Граничные случаи

**Слишком длинное сообщение:**
- Telegram ограничивает 4096 символов
- Бот автоматически разбивает ответ на части (если реализовано)
- Или обрезает с уведомлением

**Несколько tool calls подряд:**
- LLMClient обрабатывает до 5 итераций
- После 5 итераций возвращает сообщение об ошибке

**Одновременные запросы от одного пользователя:**
- Обрабатываются последовательно (aiogram)
- Контекст обновляется корректно

---

## 8. Подход к конфигурированию

### Файл .env

Все настройки приложения хранятся в `.env` файле и загружаются через Pydantic Settings.

#### Шаблон .env.example

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_PROXY_URL=https://api.your-proxy.com/v1
OPENAI_TIMEOUT=30.0
OPENAI_MODEL=gpt-4o-mini

# Bot Behavior
SYSTEM_PROMPT=Ты полезный ассистент. Отвечай на вопросы пользователя вежливо и информативно.
MAX_CONTEXT_MESSAGES=10

# Logging
LOG_LEVEL=INFO
```

### Класс Config (config.py)

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Config(BaseSettings):
    """Конфигурация приложения."""
    
    # Telegram
    telegram_bot_token: str = Field(..., description="Токен Telegram бота")
    
    # OpenAI
    openai_api_key: str = Field(..., description="API ключ OpenAI")
    openai_proxy_url: str = Field(..., description="URL прокси для OpenAI")
    openai_timeout: float = Field(default=30.0, ge=1.0, description="Таймаут для запросов к OpenAI (секунды)")
    openai_model: str = Field(default="gpt-4o-mini", description="Модель LLM")
    
    # Поведение
    system_prompt: str = Field(
        default="Ты полезный ассистент. Отвечай на вопросы пользователя вежливо и информативно.",
        description="Системный промпт для LLM"
    )
    max_context_messages: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Максимум сообщений в истории"
    )
    
    # Логирование
    log_level: str = Field(default="INFO", description="Уровень логирования")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }
    
    def validate_config(self) -> None:
        """Валидация конфигурации при старте."""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN обязателен")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY обязателен")
        if not self.openai_proxy_url:
            raise ValueError("OPENAI_PROXY_URL обязателен")
```

### Загрузка конфигурации

```python
# main.py
from src.config import Config

def main():
    # Загрузка конфигурации
    config = Config()
    
    # Валидация
    config.validate_config()
    
    # Использование
    logger.info(f"Запуск бота с моделью: {config.openai_model}")
```

### Переменные окружения в Docker

При использовании Docker можно передавать переменные через:

1. **docker-compose.yml**:
```yaml
services:
  bot:
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

2. **Файл .env** (монтируется автоматически docker-compose)

3. **Секреты Docker** (для production):
```yaml
services:
  bot:
    secrets:
      - telegram_token
      - openai_key
```

### Приоритет конфигурации

1. Переменные окружения (highest priority)
2. Файл .env
3. Дефолтные значения в Config

### Безопасность

- `.env` добавлен в `.gitignore`
- `.env.example` - шаблон без реальных токенов
- В логах не выводятся чувствительные данные
- В docker-compose можно использовать secrets

---

## 9. Подход к логгированию

### Структура логирования

Используется стандартная библиотека `logging` Python с следующей конфигурацией:

#### Настройка logger (main.py)

```python
import logging
import sys

def setup_logging(log_level: str = "INFO") -> None:
    """Настройка логирования приложения."""
    
    # Формат логов
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Базовая конфигурация
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Отключаем лишние логи от библиотек
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("aiogram").setLevel(logging.INFO)
```

### Уровни логирования

- **DEBUG**: Детальная информация для отладки
- **INFO**: Основные события (старт бота, обработка сообщений)
- **WARNING**: Предупреждения (лимиты, долгие запросы)
- **ERROR**: Ошибки (API недоступен, исключения)
- **CRITICAL**: Критические ошибки (бот не может работать)

### Логирование в модулях

#### main.py
```python
import logging

logger = logging.getLogger(__name__)

def main():
    logger.info("Запуск LLM-ассистента")
    logger.info(f"Модель: {config.openai_model}")
    logger.info(f"Макс. контекст: {config.max_context_messages}")
```

#### handlers.py
```python
import logging

logger = logging.getLogger(__name__)

async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text
    
    logger.info(f"Сообщение от пользователя {user_id}: {text[:50]}...")
    
    try:
        response = await llm_client.get_response(history)
        logger.info(f"Ответ пользователю {user_id}: {response[:50]}...")
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
```

#### llm_client.py
```python
import logging

logger = logging.getLogger(__name__)

async def get_response(self, messages: list[Message]) -> str | None:
    logger.debug(f"Запрос к LLM: {len(messages)} сообщений")
    
    try:
        response = await self.client.chat.completions.create(...)
        logger.info("Получен ответ от LLM")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка при обращении к LLM: {e}", exc_info=True)
        return None
```

#### wikipedia_tool.py
```python
import logging

logger = logging.getLogger(__name__)

async def search(self, query: str, language: str = "ru") -> str:
    logger.info(f"Поиск в Wikipedia: '{query}' ({language})")
    
    try:
        page = wiki.page(query)
        if page.exists():
            logger.info(f"Найдена статья: {page.title}")
        else:
            logger.warning(f"Статья не найдена: {query}")
    except Exception as e:
        logger.error(f"Ошибка поиска в Wikipedia: {e}")
```

### Примеры логов

#### Успешная обработка
```
2025-10-10 14:23:15 | INFO     | __main__ | Запуск LLM-ассистента
2025-10-10 14:23:15 | INFO     | __main__ | Модель: gpt-4o-mini
2025-10-10 14:23:16 | INFO     | src.bot | Бот запущен: @my_assistant_bot
2025-10-10 14:23:45 | INFO     | src.handlers | Сообщение от пользователя 123456: Привет!
2025-10-10 14:23:46 | INFO     | src.llm_client | Получен ответ от LLM
2025-10-10 14:23:46 | INFO     | src.handlers | Ответ пользователю 123456: Здравствуйте! Чем...
```

#### Обработка с Wikipedia
```
2025-10-10 14:25:30 | INFO     | src.handlers | Сообщение от пользователя 123456: Кто такой Пушкин?
2025-10-10 14:25:31 | INFO     | src.llm_client | LLM вызвал tool: search_wikipedia
2025-10-10 14:25:31 | INFO     | src.wikipedia_tool | Поиск в Wikipedia: 'Пушкин' (ru)
2025-10-10 14:25:32 | INFO     | src.wikipedia_tool | Найдена статья: Пушкин, Александр Сергеевич
2025-10-10 14:25:33 | INFO     | src.llm_client | Получен ответ от LLM
2025-10-10 14:25:33 | INFO     | src.handlers | Ответ пользователю 123456: Александр Сергеевич...
```

#### Ошибка API
```
2025-10-10 14:30:00 | INFO     | src.handlers | Сообщение от пользователя 123456: Расскажи про космос
2025-10-10 14:30:05 | ERROR    | src.llm_client | Ошибка при обращении к LLM: Connection timeout
Traceback (most recent call last):
  ...
2025-10-10 14:30:05 | ERROR    | src.handlers | Не удалось получить ответ от LLM
2025-10-10 14:30:05 | INFO     | src.handlers | Отправлено сообщение об ошибке пользователю 123456
```

### Логирование в Docker

При запуске в Docker логи выводятся в stdout и доступны через:

```bash
# Просмотр логов
docker-compose logs -f bot

# Последние 100 строк
docker-compose logs --tail=100 bot

# Логи с временем
docker logs -t <container_id>
```

### Ротация логов (опционально для production)

Для production можно добавить ротацию логов:

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "logs/bot.log",
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
```

Но для MVP достаточно логов в stdout.

---

## 10. Dockerfile и Контейнеризация

### Dockerfile (multi-stage build)

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock* ./

# Установка зависимостей
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim

# Метаданные
LABEL maintainer="your-email@example.com"
LABEL description="LLM Assistant Telegram Bot"

# Создание non-root пользователя
RUN useradd -m -u 1000 botuser

# Рабочая директория
WORKDIR /app

# Копирование установленных пакетов из builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Копирование исходного кода
COPY --chown=botuser:botuser src/ ./src/

# Переключение на non-root пользователя
USER botuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Запуск приложения
CMD ["python", "-m", "src.main"]
```

### .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/

# Tests
tests/
.pytest_cache/

# Docs
docs/

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: llm-assistant-bot
    restart: unless-stopped
    
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_PROXY_URL=${OPENAI_PROXY_URL}
      - OPENAI_MODEL=${OPENAI_MODEL:-gpt-4o-mini}
      - SYSTEM_PROMPT=${SYSTEM_PROMPT}
      - MAX_CONTEXT_MESSAGES=${MAX_CONTEXT_MESSAGES:-10}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    
    # Монтирование .env (опционально, переменные можно задать выше)
    env_file:
      - .env
    
    # Ограничения ресурсов
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    
    # Логирование
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

### Команды Docker

```bash
# Сборка образа
docker-compose build

# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down

# Пересборка и перезапуск
docker-compose up -d --build
```

### Makefile integration

```makefile
.PHONY: docker-build docker-up docker-down docker-logs

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f bot

docker-restart:
	docker-compose restart bot
```

### Оптимизация образа

1. **Multi-stage build** - минимизация размера образа
2. **Slim base image** - python:3.12-slim вместо full
3. **Layer caching** - правильный порядок COPY команд
4. **Non-root user** - безопасность
5. **.dockerignore** - исключение лишних файлов

### Безопасность

- ✅ Non-root пользователь (botuser)
- ✅ Healthcheck для мониторинга
- ✅ Ограничения ресурсов
- ✅ Секреты через переменные окружения
- ✅ Минимальный base image

---

## 11. CHANGELOG

### Формат

Проект следует стандарту [Keep a Changelog](https://keepachangelog.com/) и [Semantic Versioning](https://semver.org/).

### CHANGELOG.md

```markdown
# Changelog

Все значимые изменения проекта документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Планируется
- Поддержка голосовых сообщений
- Сохранение контекста в SQLite
- Дополнительные инструменты (погода, калькулятор)

## [0.1.0] - 2025-10-10

### Added
- Базовая интеграция с Telegram через aiogram
- Интеграция с OpenAI API через прокси
- Wikipedia tool для поиска фактической информации
- Управление контекстом диалога (in-memory)
- Команды: /start, /help, /reset
- Конфигурация через .env файл
- Логирование всех операций
- Dockerfile и docker-compose для контейнеризации
- Юнит-тесты для основных компонентов
- Документация: README, vision.md, idea.md

### Technical
- Python 3.12
- uv для управления зависимостями
- Pydantic для валидации конфигурации
- Async/await архитектура
- Function calling для инструментов

## [0.0.1] - 2025-10-09

### Added
- Инициализация проекта
- Базовая структура директорий
- Техническое видение в docs/vision.md
```

### Правила обновления CHANGELOG

#### Типы изменений:
- **Added** - новый функционал
- **Changed** - изменения существующего функционала
- **Deprecated** - функционал, который скоро удалят
- **Removed** - удаленный функционал
- **Fixed** - исправления багов
- **Security** - исправления уязвимостей

#### Процесс:
1. Все изменения сначала попадают в `[Unreleased]`
2. При релизе создается новая версия с датой
3. Версионирование: MAJOR.MINOR.PATCH
   - MAJOR: несовместимые изменения API
   - MINOR: новый функционал (обратно совместимый)
   - PATCH: исправления багов

#### Пример записи:

```markdown
## [0.2.0] - 2025-10-15

### Added
- Поддержка streaming ответов от LLM (#12)
- Новый инструмент WeatherTool для получения погоды (#15)
- Команда /stats для статистики использования (#18)

### Changed
- Увеличен дефолтный MAX_CONTEXT_MESSAGES с 10 до 15 (#14)
- Обновлена версия aiogram до 3.2.0 (#16)

### Fixed
- Исправлена ошибка при обработке длинных ответов от Wikipedia (#13)
- Корректная обработка пустых сообщений (#17)

### Security
- Обновлены зависимости с уязвимостями (#19)
```

---

## 12. Итоговая структура проекта

```
systech-aidd_mcr/
├── src/
│   ├── __init__.py
│   ├── main.py              # Точка входа, инициализация и запуск
│   ├── config.py            # Config (Pydantic Settings)
│   ├── bot.py               # TelegramBot (aiogram setup)
│   ├── handlers.py          # MessageHandler (обработка команд/сообщений)
│   ├── llm_client.py        # LLMClient (OpenAI API + function calling)
│   ├── context_manager.py   # ContextManager (история диалогов)
│   └── wikipedia_tool.py    # WikipediaTool (поиск в Wikipedia)
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_context_manager.py
│   ├── test_llm_client.py
│   ├── test_handlers.py
│   └── test_wikipedia_tool.py
│
├── docs/
│   ├── idea.md              # Концепция проекта
│   └── vision.md            # Техническое видение (этот документ)
│
├── .env                     # Переменные окружения (в .gitignore)
├── .env.example             # Шаблон переменных окружения
├── .gitignore               # Игнорируемые файлы
├── .dockerignore            # Игнорируемые файлы для Docker
├── Dockerfile               # Multi-stage Docker образ
├── docker-compose.yml       # Docker Compose конфигурация
├── pyproject.toml           # Конфигурация проекта и зависимостей (uv)
├── uv.lock                  # Lock-файл зависимостей (uv)
├── Makefile                 # Команды для разработки
├── CHANGELOG.md             # История изменений
└── README.md                # Документация для пользователей
```

### Описание файлов

#### Код приложения (src/)

- **main.py** - точка входа, создает все объекты, настраивает логирование, запускает бота
- **config.py** - Pydantic модель конфигурации, загрузка из .env
- **bot.py** - настройка aiogram Bot и Dispatcher, регистрация handlers
- **handlers.py** - обработчики команд (/start, /help, /reset) и текстовых сообщений
- **llm_client.py** - работа с OpenAI API, function calling, обработка tools
- **context_manager.py** - хранение и управление историей диалогов
- **wikipedia_tool.py** - поиск информации в Wikipedia

#### Тесты (tests/)

- **test_config.py** - тестирование загрузки и валидации конфигурации
- **test_context_manager.py** - тестирование добавления/получения/очистки истории
- **test_llm_client.py** - тестирование запросов к LLM (моки)
- **test_handlers.py** - тестирование обработчиков команд и сообщений
- **test_wikipedia_tool.py** - тестирование поиска в Wikipedia

#### Конфигурация

- **.env** - реальные токены и настройки (НЕ коммитится)
- **.env.example** - шаблон без реальных токенов
- **pyproject.toml** - зависимости, метаданные проекта, настройки инструментов
- **uv.lock** - lock-файл зависимостей (коммитится в git)
- **Makefile** - удобные команды для разработки

#### Docker

- **Dockerfile** - multi-stage образ с оптимизацией
- **docker-compose.yml** - конфигурация для запуска
- **.dockerignore** - исключаемые файлы

#### Документация

- **README.md** - инструкция по установке и использованию
- **CHANGELOG.md** - история изменений
- **docs/idea.md** - концепция проекта
- **docs/vision.md** - техническое видение

---

## 13. Makefile

```makefile
.PHONY: help install dev run test lint format clean docker-build docker-up docker-down docker-logs

# Цвета для вывода
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	uv sync --no-dev

dev: ## Установить зависимости для разработки
	@echo "$(GREEN)Установка dev зависимостей...$(NC)"
	uv sync

run: ## Запустить бота локально
	@echo "$(GREEN)Запуск бота...$(NC)"
	python -m src.main

test: ## Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	pytest tests/ -v --cov=src --cov-report=term-missing

test-quick: ## Быстрые тесты (без coverage)
	@echo "$(GREEN)Быстрые тесты...$(NC)"
	pytest tests/ -v

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверка кода...$(NC)"
	ruff check src/ tests/

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	ruff format src/ tests/
	ruff check --fix src/ tests/

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очистка...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/

# Docker команды
docker-build: ## Собрать Docker образ
	@echo "$(GREEN)Сборка Docker образа...$(NC)"
	docker-compose build

docker-up: ## Запустить в Docker
	@echo "$(GREEN)Запуск в Docker...$(NC)"
	docker-compose up -d

docker-down: ## Остановить Docker контейнеры
	@echo "$(GREEN)Остановка Docker...$(NC)"
	docker-compose down

docker-logs: ## Показать логи Docker
	docker-compose logs -f bot

docker-restart: ## Перезапустить Docker контейнер
	@echo "$(GREEN)Перезапуск Docker...$(NC)"
	docker-compose restart bot

docker-rebuild: ## Пересобрать и перезапустить
	@echo "$(GREEN)Пересборка и перезапуск...$(NC)"
	docker-compose up -d --build

# Комплексные команды
check: lint test ## Проверка кода и тесты

setup: ## Первоначальная настройка проекта
	@echo "$(GREEN)Настройка проекта...$(NC)"
	uv sync
	@echo "$(GREEN)Проект настроен!$(NC)"
	@echo "Не забудьте создать .env файл на основе .env.example"

all: clean format lint test ## Полная проверка проекта
	@echo "$(GREEN)Все проверки пройдены!$(NC)"
```

### Использование Makefile

```bash
# Первая настройка проекта
uv sync           # Установка зависимостей
make setup

# Разработка
make run          # Запустить бота локально
make test         # Запустить тесты
make lint         # Проверить код
make format       # Отформатировать код

# Docker
make docker-build # Собрать образ
make docker-up    # Запустить
make docker-logs  # Посмотреть логи
make docker-down  # Остановить

# Комплексные команды
make check        # Линтер + тесты
make all          # Очистка + форматирование + линтер + тесты
make clean        # Очистить временные файлы

# Справка
make help         # Показать все команды
```

---

## 14. pyproject.toml

```toml
[project]
name = "systech-aidd-mcr"
version = "0.1.0"
description = "LLM Assistant Telegram Bot with Wikipedia integration"
authors = [
    {name = "Your Name", email = "your-email@example.com"}
]
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}

dependencies = [
    "aiogram>=3.13.0",
    "openai>=1.51.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.5.0",
    "python-dotenv>=1.0.0",
    "wikipedia-api>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
asyncio_mode = "auto"
addopts = "-v --strict-markers"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

---

## 15. Итоговый чеклист для MVP

### Обязательные компоненты

- [x] **Технологии определены**: Python 3.12, uv, aiogram, openai, make
- [x] **Принципы разработки**: KISS, ООП, 1 класс = 1 файл
- [x] **Структура проекта**: Плоская, понятная структура
- [x] **Архитектура**: 5 основных классов с четкими ответственностями
- [x] **Модель данных**: Pydantic модели для всех структур
- [x] **Работа с LLM**: OpenAI через прокси + Wikipedia tool
- [x] **Сценарии**: 8 основных сценариев работы
- [x] **Конфигурация**: .env + Pydantic Settings
- [x] **Логирование**: Стандартный logging с четкой структурой
- [x] **Docker**: Multi-stage Dockerfile + docker-compose
- [x] **CHANGELOG**: Keep a Changelog формат
- [x] **Makefile**: Все основные команды
- [x] **pyproject.toml**: Современная конфигурация с uv

### Файлы для создания

```
✅ docs/vision.md            # Создан (этот документ)
⬜ docs/idea.md              # Уже существует
⬜ src/main.py
⬜ src/config.py
⬜ src/bot.py
⬜ src/handlers.py
⬜ src/llm_client.py
⬜ src/context_manager.py
⬜ src/wikipedia_tool.py
⬜ tests/test_*.py
⬜ .env.example
⬜ .gitignore
⬜ .dockerignore
⬜ Dockerfile
⬜ docker-compose.yml
⬜ pyproject.toml
⬜ uv.lock                   # Генерируется автоматически через uv sync
⬜ Makefile
⬜ CHANGELOG.md
⬜ README.md
```

---

## 16. Следующие шаги

### Фаза 1: Создание структуры (День 1)
1. Создать все директории и пустые файлы
2. Настроить .gitignore, .dockerignore, .env.example
3. Создать pyproject.toml и Makefile
4. Инициализировать git репозиторий

### Фаза 2: Базовая реализация (День 1-2)
1. Реализовать Config (config.py)
2. Реализовать ContextManager (context_manager.py)
3. Реализовать WikipediaTool (wikipedia_tool.py)
4. Написать тесты для этих компонентов

### Фаза 3: Интеграция LLM (День 2-3)
1. Реализовать LLMClient (llm_client.py)
2. Интегрировать Wikipedia tool через function calling
3. Написать тесты с моками OpenAI API

### Фаза 4: Telegram Bot (День 3-4)
1. Реализовать MessageHandler (handlers.py)
2. Реализовать TelegramBot (bot.py)
3. Реализовать main.py с логированием
4. Написать интеграционные тесты

### Фаза 5: Финализация (День 4-5)
1. Создать Dockerfile и docker-compose.yml
2. Написать README.md
3. Создать CHANGELOG.md
4. Протестировать локально и в Docker
5. Документировать установку и использование

### Критерий готовности MVP

✅ Бот запускается локально и в Docker  
✅ Обрабатывает команды /start, /help, /reset  
✅ Отвечает на вопросы через OpenAI API  
✅ Использует Wikipedia для поиска информации  
✅ Хранит контекст диалога  
✅ Логирует все операции  
✅ Покрыт базовыми тестами (>70% coverage)  
✅ Задокументирован (README, vision)  

### Фаза 6: Technical Debt & Качество (Refactoring Branch)
**После завершения MVP - работа по [tasklist_tech_dept.md](tasklist_tech_dept.md)**

1. **TechDebt-1**: Исправление падающих тестов
   - Адаптация тестов после рефакторинга
   - 0 failed tests обязательно

2. **TechDebt-2**: Добавление mypy + type checking
   - Статическая типизация
   - Команда `make type-check`

3. **TechDebt-3**: Устранение magic numbers
   - Все константы → Config
   - DRY принцип

4. **TechDebt-4**: Рефакторинг Tools → Protocol
   - Создание `src/tools/` с единым интерфейсом
   - Устранение дублирования

5. **TechDebt-5**: Разделение LLMClient (SOLID)
   - `src/llm/client.py` - OpenAI wrapper
   - `src/llm/orchestrator.py` - tool calling
   - Single Responsibility для каждого класса

6. **TechDebt-6**: Повышение coverage до 85%+
   - Покрытие bot.py, main.py
   - Integration tests
   - Все критичные пути покрыты

**Целевые метрики после tech debt:**
- Coverage: >= 85%
- Tests: 0 failed, 70+ passed
- Линтеры: ruff + mypy ✓
- SOLID: все принципы соблюдены
- DRY: нет дублирования

---

## 17. Эволюция архитектуры

### MVP архитектура (Фазы 1-5)
```
src/
├── main.py
├── config.py
├── bot.py
├── handlers.py
├── llm_client.py (монолитный)
├── context_manager.py
├── wikipedia_tool.py
├── datetime_tool.py
└── websearch_tool.py
```

### Production-ready архитектура (после Фазы 6)
```
src/
├── main.py
├── config.py (расширенная с константами)
├── bot.py
├── handlers.py
├── llm_client.py (фасад для обратной совместимости)
├── context_manager.py
│
├── llm/ (SOLID: разделение ответственности)
│   ├── client.py (OpenAI API wrapper)
│   └── orchestrator.py (tool calling logic)
│
└── tools/ (DRY: единый интерфейс)
    ├── base.py (Tool Protocol)
    ├── wikipedia.py
    ├── datetime.py
    └── websearch.py
```

**Преимущества рефакторинга:**
- ✅ Легче добавлять новые tools (Protocol)
- ✅ Легче тестировать (мелкие компоненты)
- ✅ Легче поддерживать (SOLID)
- ✅ Меньше багов (type checking + coverage)

---

**Документ завершен**: 10 октября 2025  
**Последнее обновление**: 11 октября 2025  
**Версия**: 2.0  
**Статус**: Готово к реализации ✅ (MVP + Tech Debt Roadmap)

