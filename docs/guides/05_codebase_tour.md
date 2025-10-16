# 🗺️ Codebase Tour - Тур по репозиторию

> Где что находится и за что отвечает

---

## 📂 Структура проекта

```
systech-aidd_mcr/
├── 📄 pyproject.toml          # Зависимости и конфигурация (uv)
├── 📄 Makefile                # Команды разработки
├── 📄 .env                    # Секреты (не в git)
├── 📄 .env.example            # Шаблон .env
├── 📄 uv.lock                 # Lock-файл зависимостей
│
├── 📁 src/                    # Исходный код приложения
├── 📁 tests/                  # Тесты
├── 📁 docs/                   # Документация
└── 📁 prompts/                # Системные промпты для ролей
```

---

## 🎯 Корневые файлы

### `pyproject.toml`
**Назначение:** Конфигурация проекта, зависимости, настройки инструментов

```toml
[project]
name = "systech-aidd-mcr"
version = "0.1.0"
requires-python = ">=3.12,<3.13"

dependencies = [
    "aiogram>=3.13.0",        # Telegram бот
    "openai>=1.51.0",         # OpenAI API
    "pydantic>=2.9.0",        # Валидация
    "wikipedia-api>=0.7.0",   # Wikipedia
    "duckduckgo-search>=8.1.1", # Веб-поиск
    # ...
]

[tool.ruff]      # Линтер настройки
[tool.pytest]    # Тесты настройки
[tool.mypy]      # Type checker настройки
```

### `Makefile`
**Назначение:** Автоматизация команд разработки

```makefile
make run          # Запустить бота
make test         # Тесты + coverage
make lint         # Проверка кода (ruff)
make type-check   # Проверка типов (mypy)
make format       # Форматирование кода
make clean        # Очистка кэша
```

### `.env` (создается вручную)
**Назначение:** Секреты и конфигурация

```bash
TELEGRAM_BOT_TOKEN=...
OPENAI_API_KEY=...
OPENAI_PROXY_URL=...
# ...
```

---

## 📁 src/ - Исходный код

### 🚀 `src/main.py`
**Назначение:** Точка входа, инициализация всего приложения

```python
# Что здесь происходит:
1. setup_logging() - настройка логирования
2. Config() - загрузка конфигурации из .env
3. Создание компонентов:
   - ContextManager
   - LLMClient (tools создаются автоматически)
   - MessageHandler
   - TelegramBot
4. bot.start() - запуск polling
```

**Когда смотреть:** Чтобы понять как стартует приложение

---

### ⚙️ `src/config.py`
**Назначение:** Pydantic конфигурация, загрузка .env и промптов

```python
class Config(BaseSettings):
    # Telegram
    telegram_bot_token: str

    # OpenAI
    openai_api_key: str
    openai_proxy_url: str
    openai_model: str = "gpt-4o-mini"

    # Роль бота
    system_prompt_file: str = "prompts/default.txt"
    role_name: str
    role_description: str

    # Лимиты
    max_context_messages: int = 10
    max_tool_iterations: int = 10
    max_websearch_calls: int = 2

    # Загруженный промпт
    system_prompt: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Загрузка промпта из файла
        self.system_prompt = Path(self.system_prompt_file).read_text()
```

**Когда смотреть:**
- Добавить новый параметр конфигурации
- Понять какие есть настройки

---

### 🤖 `src/bot.py`
**Назначение:** Настройка Telegram бота (aiogram)

```python
class TelegramBot:
    def __init__(self, config: Config, message_handler: MessageHandler):
        # Создать Bot
        self.bot = Bot(token=config.telegram_bot_token)

        # Создать Dispatcher + Router
        self.dispatcher = Dispatcher()
        self.router = Router()

        # Зарегистрировать handlers
        self.register_handlers()

    def register_handlers(self):
        # Команды
        self.router.message(Command("start"))(...)
        self.router.message(Command("help"))(...)
        self.router.message(Command("role"))(...)
        self.router.message(Command("reset"))(...)

        # Текст
        self.router.message(F.text)(...)

    async def start(self):
        # Infinite polling
        await self.dispatcher.start_polling(self.bot)
```

**Когда смотреть:**
- Добавить новую команду
- Понять routing сообщений

---

### 📝 `src/handlers.py`
**Назначение:** Обработчики команд и сообщений

```python
class MessageHandler:
    def __init__(
        self,
        config: Config,
        context_manager: ContextManager,
        llm_client: LLMClient
    ):
        self.config = config
        self.context = context_manager
        self.llm = llm_client

    async def handle_start(self, message: Message):
        """Команда /start"""
        await message.answer(WELCOME_TEXT)

    async def handle_help(self, message: Message):
        """Команда /help"""
        await message.answer(HELP_TEXT)

    async def handle_role(self, message: Message):
        """Команда /role - показать роль бота"""
        text = (
            f"🤖 Моя роль\n\n"
            f"Название: {self.config.role_name}\n"
            f"Описание: {self.config.role_description}\n"
        )
        await message.answer(text)

    async def handle_reset(self, message: Message):
        """Команда /reset - очистить историю"""
        user_id = message.from_user.id
        self.context.clear_history(user_id)
        await message.answer("✅ История очищена")

    async def handle_message(self, message: Message):
        """Обработка текстовых сообщений"""
        user_id = message.from_user.id
        text = message.text

        # Добавить в контекст
        self.context.add_message(user_id, "user", text)

        # Получить историю
        history = self.context.get_history(user_id)

        # Запрос к LLM
        response = await self.llm.get_response(history)

        # Добавить ответ в контекст
        self.context.add_message(user_id, "assistant", response)

        # Отправить пользователю
        await message.answer(response)
```

**Когда смотреть:**
- Добавить новую команду
- Изменить логику обработки сообщений

---

### 💾 `src/context_manager.py`
**Назначение:** Управление историей диалогов (in-memory)

```python
class Message(BaseModel):
    """Одно сообщение в диалоге."""
    role: Literal["user", "assistant", "system"]
    content: str

class UserContext(BaseModel):
    """Контекст одного пользователя."""
    user_id: int
    messages: list[Message] = []

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def get_messages(self, limit: int) -> list[Message]:
        return self.messages[-limit:] if limit > 0 else self.messages

    def clear(self) -> None:
        self.messages = []

class ContextManager:
    """Управление контекстами всех пользователей."""

    def __init__(self, config: Config):
        self.config = config
        self.contexts: dict[int, UserContext] = {}

    def add_message(self, user_id: int, role: str, content: str):
        # Создать контекст если нет
        if user_id not in self.contexts:
            self.contexts[user_id] = UserContext(user_id=user_id)

        # Добавить сообщение
        self.contexts[user_id].add_message(role, content)

        # Обрезать до лимита
        self._trim_history(user_id)

    def get_history(self, user_id: int) -> list[Message]:
        if user_id not in self.contexts:
            return []
        return self.contexts[user_id].get_messages(
            limit=self.config.max_context_messages
        )

    def clear_history(self, user_id: int):
        if user_id in self.contexts:
            self.contexts[user_id].clear()
```

**Когда смотреть:**
- Понять как хранится история
- Изменить логику обрезки контекста

---

### 🧠 `src/llm_client.py`
**Назначение:** Фасад для работы с LLM (обратная совместимость)

```python
class LLMClient:
    """Фасад для работы с LLM."""

    def __init__(self, config: Config, tools: list[Tool] | None = None):
        self.config = config

        # Создать OpenAI клиент
        self.openai_client = OpenAIClient(config)

        # Создать или получить tools
        self.tools = tools or self._get_default_tools()

        # Создать оркестратор
        self.orchestrator = ToolOrchestrator(
            self.openai_client,
            self.tools,
            config
        )

    def _get_default_tools(self) -> list[Tool]:
        """Получить дефолтные tools."""
        return [
            WikipediaTool(self.config),
            DateTimeTool(),
            WebSearchTool()
        ]

    async def get_response(self, messages: list[Message]) -> str | None:
        """Получить ответ от LLM."""
        return await self.orchestrator.process_with_tools(messages)
```

**Когда смотреть:**
- Добавить новый tool
- Понять как tools подключаются

---

## 📁 src/llm/ - LLM компоненты

### 🌐 `src/llm/client.py`
**Назначение:** Чистый wrapper над OpenAI API

```python
class OpenAIClient:
    """Обертка над OpenAI API."""

    def __init__(self, config: Config):
        # HTTP клиент с прокси
        http_client = httpx.AsyncClient(
            proxy=config.openai_proxy_url,
            timeout=config.openai_timeout
        )

        # OpenAI клиент
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            http_client=http_client
        )
        self.config = config

    async def create_completion(
        self,
        messages: list[dict],
        tools: list[dict] | None = None
    ):
        """Создать completion."""
        return await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=messages,
            tools=tools,
            max_completion_tokens=self.config.max_completion_tokens
        )
```

**Когда смотреть:**
- Изменить параметры OpenAI запроса
- Добавить retry логику

---

### ⚙️ `src/llm/orchestrator.py`
**Назначение:** Tool calling loop

```python
class ToolOrchestrator:
    """Управление tool calling циклом."""

    def __init__(
        self,
        openai_client: OpenAIClient,
        tools: list[Tool],
        config: Config
    ):
        self.openai_client = openai_client
        self.tools = tools
        self.config = config

    async def process_with_tools(
        self,
        messages: list[Message]
    ) -> str | None:
        """Обработать запрос с tool calling."""

        # Подготовить сообщения
        request_messages = [
            {"role": "system", "content": self.config.system_prompt},
            *[msg.model_dump() for msg in messages]
        ]

        # Получить схемы tools
        tools_schema = self._get_tools_schema()

        # Tool calling loop
        websearch_count = 0
        for iteration in range(self.config.max_tool_iterations):
            # Запрос к OpenAI
            response = await self.openai_client.create_completion(
                messages=request_messages,
                tools=tools_schema
            )

            message = response.choices[0].message

            # Если нет tool_calls - вернуть ответ
            if not message.tool_calls:
                return message.content

            # Выполнить tool_calls
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                # Лимит веб-поиска
                if function_name == "web_search":
                    if websearch_count >= self.config.max_websearch_calls:
                        result = "Лимит веб-поиска превышен"
                    else:
                        websearch_count += 1
                        result = await self._execute_tool(function_name, arguments)
                else:
                    result = await self._execute_tool(function_name, arguments)

                # Добавить результат в messages
                request_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

        # Превышен лимит итераций
        return "Превышен лимит итераций обработки"

    def _get_tools_schema(self) -> list[dict]:
        """Получить схемы всех tools."""
        return [tool.get_schema() for tool in self.tools]

    async def _execute_tool(
        self,
        function_name: str,
        arguments: dict
    ) -> str:
        """Выполнить tool по имени."""
        for tool in self.tools:
            schema = tool.get_schema()
            if schema["function"]["name"] == function_name:
                return await tool.execute(**arguments)

        return f"Ошибка: tool '{function_name}' не найден"
```

**Когда смотреть:**
- Изменить логику tool calling
- Добавить новые лимиты
- Понять как работает цикл

---

## 📁 src/tools/ - Инструменты

### 🔧 `src/tools/base.py`
**Назначение:** Protocol интерфейс для всех tools

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

**Когда смотреть:**
- Создать новый tool
- Понять интерфейс tools

---

### 📚 `src/tools/wikipedia.py`
**Назначение:** Поиск в Wikipedia

```python
class WikipediaTool:
    def __init__(self, config: Config):
        self.config = config
        self.wiki_ru = wikipediaapi.Wikipedia('ru', 'LLM-Bot/1.0')
        self.wiki_en = wikipediaapi.Wikipedia('en', 'LLM-Bot/1.0')

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "search_wikipedia",
                "description": "Поиск информации в Wikipedia",
                "parameters": {...}
            }
        }

    async def execute(self, query: str, language: str = "ru") -> str:
        return await self.search(query, language)

    async def search(self, query: str, language: str = "ru") -> str:
        wiki = self.wiki_ru if language == "ru" else self.wiki_en
        page = wiki.page(query)

        if not page.exists():
            return f"Статья '{query}' не найдена"

        summary = page.summary[:500]
        return f"{summary}...\n\n🔗 Источник: {page.fullurl}"
```

---

### 🕐 `src/tools/datetime.py`
**Назначение:** Текущая дата и время

```python
class DateTimeTool:
    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "get_current_datetime",
                "description": "Получить текущую дату и время",
                "parameters": {...}
            }
        }

    async def execute(
        self,
        timezone: str = "Europe/Moscow",
        format: str = "full"
    ) -> str:
        return await self.get_current_datetime(timezone, format)

    async def get_current_datetime(...) -> str:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime(...)
```

---

### 🔍 `src/tools/websearch.py`
**Назначение:** Веб-поиск через DuckDuckGo

```python
class WebSearchTool:
    def __init__(self):
        self.ddgs = AsyncDDGS()

    def get_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Поиск в интернете",
                "parameters": {...}
            }
        }

    async def execute(self, query: str, max_results: int = 3) -> str:
        return await self.search(query, max_results)

    async def search(self, query: str, max_results: int = 3) -> str:
        results = await self.ddgs.atext(query, max_results=max_results)
        # Форматировать результаты
        return formatted_results
```

---

## 📁 tests/ - Тесты

### Структура тестов

```
tests/
├── test_config.py              # Тесты Config
├── test_context_manager.py     # Тесты ContextManager
├── test_handlers.py            # Тесты MessageHandler
├── test_llm_client.py          # Тесты LLMClient
├── test_bot.py                 # Тесты TelegramBot
├── test_main.py                # Тесты main()
├── test_wikipedia_tool.py      # Тесты WikipediaTool
├── test_datetime_tool.py       # Тесты DateTimeTool
└── test_websearch_tool.py      # Тесты WebSearchTool
```

**Принцип:** 1 модуль = 1 тестовый файл

---

## 📁 prompts/ - Системные промпты

```
prompts/
├── default.txt              # Универсальный ассистент
├── it_consultant.txt        # IT-консультант
├── personal_assistant.txt   # Персональный помощник
└── python_tutor.txt         # Учитель Python
```

**Создать свою роль:**
1. Создать файл `prompts/my_role.txt`
2. Обновить `.env`: `SYSTEM_PROMPT_FILE=prompts/my_role.txt`

---

## 🔍 Где искать что

| Задача | Файл |
|--------|------|
| Добавить команду боту | `src/handlers.py` + `src/bot.py` |
| Изменить модель LLM | `.env` (OPENAI_MODEL) |
| Добавить новый tool | `src/tools/my_tool.py` + `src/llm_client.py` |
| Изменить лимит контекста | `.env` (MAX_CONTEXT_MESSAGES) |
| Настроить роль бота | `.env` + `prompts/role.txt` |
| Логирование | `src/main.py` (setup_logging) |
| Параметры OpenAI | `src/llm/client.py` |
| Tool calling loop | `src/llm/orchestrator.py` |

---

## 📚 Дополнительно

**Архитектура:** [02_architecture_overview.md](02_architecture_overview.md)
**Модель данных:** [03_data_model.md](03_data_model.md)
**Интеграции:** [04_integrations.md](04_integrations.md)
**Конфигурация:** [06_configuration.md](06_configuration.md)


