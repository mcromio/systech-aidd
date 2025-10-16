# 🎨 Visual Architecture - Визуальная архитектура проекта

> Комплексная визуализация с разных точек зрения

---

## 📋 Содержание

1. [High-Level Architecture](#1-high-level-architecture)
2. [Component Structure](#2-component-structure)
3. [Data Flow](#3-data-flow)
4. [Class Diagram](#4-class-diagram)
5. [Integration View](#5-integration-view)
6. [State Management](#6-state-management)
7. [Message Processing Pipeline](#7-message-processing-pipeline)
8. [Tool Calling Flow](#8-tool-calling-flow)
9. [Deployment View](#9-deployment-view)
10. [Development Workflow](#10-development-workflow)
11. [Testing Structure](#11-testing-structure)
12. [Dependencies Graph](#12-dependencies-graph)

---

## 1️⃣ High-Level Architecture

### Общая архитектура системы

```mermaid
flowchart TB
    User1[User 1]
    User2[User 2]
    TG[Telegram Bot API]

    Bot[TelegramBot]
    Handler[MessageHandler]
    Context[ContextManager]
    LLMClient[LLMClient]

    OpenAIClient[OpenAIClient]
    Orchestrator[ToolOrchestrator]

    Wiki[WikipediaTool]
    DateTime[DateTimeTool]
    WebSearch[WebSearchTool]

    Config[Config]

    OpenAI[OpenAI API]
    WikiAPI[Wikipedia API]
    DDG[DuckDuckGo]

    User1 --> TG
    User2 --> TG
    TG <--> Bot
    Bot --> Handler
    Handler --> Context
    Handler --> LLMClient

    LLMClient --> OpenAIClient
    LLMClient --> Orchestrator
    Orchestrator --> OpenAIClient

    Orchestrator --> Wiki
    Orchestrator --> DateTime
    Orchestrator --> WebSearch

    Wiki --> WikiAPI
    WebSearch --> DDG
    OpenAIClient --> OpenAI

    Config -.-> Bot
    Config -.-> Handler
    Config -.-> LLMClient

    style User1 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style User2 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style TG fill:#0088cc,stroke:#006699,color:#fff
    style Bot fill:#2196F3,stroke:#1565C0,color:#fff
    style Handler fill:#FF9800,stroke:#E65100,color:#fff
    style Context fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style LLMClient fill:#F44336,stroke:#C62828,color:#fff
    style OpenAIClient fill:#E91E63,stroke:#AD1457,color:#fff
    style Orchestrator fill:#E91E63,stroke:#AD1457,color:#fff
    style Config fill:#00BCD4,stroke:#00838F,color:#fff
```

---

## 2️⃣ Component Structure

### Структура модулей и зависимости

```mermaid
flowchart LR
    Main[main.py]
    Config[config.py]
    Bot[bot.py]
    Handler[handlers.py]
    Context[context_manager.py]

    LLMClient[llm_client.py]
    OpenAIClient[llm/client.py]
    Orchestrator[llm/orchestrator.py]

    Base[tools/base.py]
    Wiki[tools/wikipedia.py]
    DT[tools/datetime.py]
    Web[tools/websearch.py]

    Main --> Config
    Main --> Bot
    Main --> Handler
    Main --> Context
    Main --> LLMClient

    Bot --> Handler
    Handler --> Context
    Handler --> LLMClient

    LLMClient --> OpenAIClient
    LLMClient --> Orchestrator
    Orchestrator --> OpenAIClient
    Orchestrator --> Base

    Wiki -.-> Base
    DT -.-> Base
    Web -.-> Base

    Config -.-> Bot
    Config -.-> Handler
    Config -.-> Context
    Config -.-> LLMClient

    style Main fill:#F44336,stroke:#C62828,color:#fff
    style Config fill:#00BCD4,stroke:#00838F,color:#fff
    style Bot fill:#2196F3,stroke:#1565C0,color:#fff
    style Handler fill:#FF9800,stroke:#E65100,color:#fff
    style LLMClient fill:#F44336,stroke:#C62828,color:#fff
```

---

## 3️⃣ Data Flow

### Поток данных через систему

```mermaid
sequenceDiagram
    participant User
    participant TG as Telegram
    participant Bot
    participant Handler
    participant Context
    participant LLM
    participant Orch as Orchestrator
    participant AI as OpenAI
    participant Tool

    User->>TG: Send message
    TG->>Bot: Update event
    Bot->>Handler: handle_message

    Handler->>Context: add_message user
    Handler->>Context: get_history
    Context-->>Handler: messages list

    Handler->>LLM: get_response
    LLM->>Orch: process_with_tools

    loop Tool Calling Loop
        Orch->>AI: create_completion
        AI-->>Orch: response + tool_calls

        alt Has tool_calls
            Orch->>Tool: execute tool
            Tool-->>Orch: result
        else No tool_calls
            Orch-->>LLM: final response
        end
    end

    LLM-->>Handler: response text
    Handler->>Context: add_message assistant
    Handler->>Bot: send_message
    Bot->>TG: Send response
    TG->>User: Display message
```

---

## 4️⃣ Class Diagram

### Структура классов и их взаимосвязи

```mermaid
classDiagram
    class Config {
        +str telegram_bot_token
        +str openai_api_key
        +str system_prompt
        +int max_context_messages
        +validate_config()
    }

    class Message {
        +str role
        +str content
    }

    class UserContext {
        +int user_id
        +list messages
        +add_message()
        +get_messages()
    }

    class ContextManager {
        -dict contexts
        +add_message()
        +get_history()
    }

    class MessageHandler {
        +handle_start()
        +handle_message()
    }

    class LLMClient {
        +get_response()
    }

    class OpenAIClient {
        +create_completion()
    }

    class ToolOrchestrator {
        +process_with_tools()
    }

    class Tool {
        <<interface>>
        +get_schema()
        +execute()
    }

    class WikipediaTool {
        +search()
    }

    ContextManager *-- UserContext
    UserContext *-- Message
    MessageHandler --> ContextManager
    MessageHandler --> LLMClient
    LLMClient --> OpenAIClient
    LLMClient --> ToolOrchestrator
    ToolOrchestrator --> Tool
    WikipediaTool ..|> Tool
```

---

## 5️⃣ Integration View

### Внешние интеграции

```mermaid
flowchart TB
    Core[Core Application]

    Aiogram[aiogram 3.x]
    TelegramAPI[Telegram Bot API]

    AsyncOpenAI[AsyncOpenAI]
    Proxy[HTTP Proxy]
    OpenAI[OpenAI API]

    WikiLib[wikipedia-api]
    WikiRU[Russian Wikipedia]

    DDGS[duckduckgo-search]
    DDGSearch[DuckDuckGo]

    PyTZ[pytz]

    Core --> Aiogram
    Aiogram --> TelegramAPI

    Core --> AsyncOpenAI
    AsyncOpenAI --> Proxy
    Proxy --> OpenAI

    Core --> WikiLib
    WikiLib --> WikiRU

    Core --> DDGS
    DDGS --> DDGSearch

    Core --> PyTZ

    style Core fill:#2196F3,stroke:#1565C0,color:#fff
    style Aiogram fill:#0088cc,stroke:#006699,color:#fff
    style AsyncOpenAI fill:#10a37f,stroke:#0d8c6a,color:#fff
    style WikiLib fill:#000000,stroke:#333333,color:#fff
    style DDGS fill:#de5833,stroke:#c14a2a,color:#fff
```

---

## 6️⃣ State Management

### Управление состоянием диалога

```mermaid
stateDiagram-v2
    [*] --> NewUser
    NewUser --> ActiveDialog: Create Context

    state ActiveDialog {
        [*] --> Receiving
        Receiving --> Processing
        Processing --> Responding
        Responding --> Receiving
    }

    ActiveDialog --> Trimmed: Max messages
    Trimmed --> ActiveDialog: Remove old

    ActiveDialog --> Cleared: Reset command
    Cleared --> ActiveDialog

    ActiveDialog --> [*]: Bot restart
```

---

## 7️⃣ Message Processing Pipeline

### Пайплайн обработки сообщения

```mermaid
flowchart TD
    Start([Message])
    Parse[Parse]

    CheckCmd{Command?}

    CmdStart[handle_start]
    CmdHelp[handle_help]
    CmdRole[handle_role]
    CmdReset[handle_reset]
    HandleMsg[handle_message]

    AddUser[Add User Msg]
    GetHist[Get History]
    CallLLM[Call LLM]

    Loop{Iteration?}
    APICall[API Call]
    CheckTools{Tools?}
    ExecTools[Execute]

    Extract[Extract]
    AddAssist[Add Assistant]
    Send[Send]
    End([Done])

    Start --> Parse
    Parse --> CheckCmd

    CheckCmd -->|/start| CmdStart
    CheckCmd -->|/help| CmdHelp
    CheckCmd -->|/role| CmdRole
    CheckCmd -->|/reset| CmdReset
    CheckCmd -->|text| HandleMsg

    CmdStart --> Send
    CmdHelp --> Send
    CmdRole --> Send
    CmdReset --> Send

    HandleMsg --> AddUser
    AddUser --> GetHist
    GetHist --> CallLLM
    CallLLM --> Loop

    Loop -->|yes| APICall
    Loop -->|no| Extract

    APICall --> CheckTools
    CheckTools -->|yes| ExecTools
    CheckTools -->|no| Extract
    ExecTools --> Loop

    Extract --> AddAssist
    AddAssist --> Send
    Send --> End

    style Start fill:#4CAF50,stroke:#2E7D32,color:#fff
    style End fill:#4CAF50,stroke:#2E7D32,color:#fff
    style CheckCmd fill:#FF9800,stroke:#E65100,color:#fff
    style CheckTools fill:#2196F3,stroke:#1565C0,color:#fff
```

---

## 8️⃣ Tool Calling Flow

### Детальный flow вызова tools

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant AI as OpenAI
    participant W as Wikipedia
    participant D as DateTime

    Note over O: Iteration 1
    O->>AI: messages + tools
    AI-->>O: tool_call search
    O->>W: execute query
    W-->>O: result

    Note over O: Iteration 2
    O->>AI: messages + result
    AI-->>O: tool_call datetime
    O->>D: execute
    D-->>O: current time

    Note over O: Iteration 3
    O->>AI: messages + result
    AI-->>O: final text
    O-->>O: return
```

---

## 9️⃣ Deployment View

### Архитектура развертывания

```mermaid
flowchart TB
    Dev[Developer Machine]
    Python[Python 3.12]
    UV[uv Package Manager]
    EnvFile[.env Configuration]

    Tests[pytest + ruff + mypy]

    Docker[Docker Container]
    Compose[docker-compose]

    TG[Telegram API]
    OAPI[OpenAI API]
    Wiki[Wikipedia]
    DDG[DuckDuckGo]

    Dev --> Python
    Dev --> UV
    Dev --> EnvFile
    Python --> Tests

    Dev -.future.-> Docker
    Docker --> Compose

    Python --> TG
    Python --> OAPI
    Python --> Wiki
    Python --> DDG

    style Dev fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Tests fill:#FF9800,stroke:#E65100,color:#fff
    style Docker fill:#2196F3,stroke:#1565C0,color:#fff
```

---

## 🔟 Development Workflow

### Процесс разработки TDD

```mermaid
flowchart LR
    RED[Write Test]
    GREEN[Write Code]
    REFACTOR[Refactor]

    Format[Format]
    Lint[Lint]
    Type[Type Check]
    Test[Run Tests]

    Branch[Branch]
    Commit[Commit]
    Push[Push]
    Review[Review]
    Merge[Merge]

    RED --> GREEN
    GREEN --> REFACTOR
    REFACTOR --> Format
    Format --> Lint
    Lint --> Type
    Type --> Test
    Test --> Branch
    Branch --> Commit
    Commit --> Push
    Push --> Review
    Review --> Merge
    Merge -.-> RED

    style RED fill:#F44336,stroke:#C62828,color:#fff
    style GREEN fill:#4CAF50,stroke:#2E7D32,color:#fff
    style REFACTOR fill:#2196F3,stroke:#1565C0,color:#fff
    style Merge fill:#9C27B0,stroke:#6A1B9A,color:#fff
```

---

## 1️⃣1️⃣ Testing Structure

### Покрытие тестами по модулям

**Общее покрытие: 78%**

| Модуль | Coverage | Статус |
|--------|----------|--------|
| context_manager.py | 100% | ✅ Excellent |
| llm_client.py | 100% | ✅ Excellent |
| config.py | 96% | ✅ Great |
| handlers.py | 93% | ✅ Great |
| wikipedia.py | 92% | ✅ Great |
| orchestrator.py | 87% | ✅ Good |
| websearch.py | 83% | ✅ Good |
| datetime.py | 82% | ✅ Good |
| client.py | 72% | ⚠️ Needs work |
| bot.py | 0% | ❌ Not covered |
| main.py | 0% | ❌ Not covered |

### Тестовая пирамида

```mermaid
flowchart TB
    E2E[E2E Tests: 0 tests]
    Integration[Integration: ~10 tests]
    Unit[Unit Tests: ~45 tests]

    Unit --> Integration
    Integration --> E2E

    style Unit fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Integration fill:#FF9800,stroke:#E65100,color:#fff
    style E2E fill:#F44336,stroke:#C62828,color:#fff
```

**Всего: 55 тестов, 0 failed ✅**

---

## 1️⃣2️⃣ Dependencies Graph

### Граф зависимостей проекта

```mermaid
flowchart TD
    SRC[src/]

    Aiogram[aiogram 3.13+]
    OpenAI[openai 1.51+]
    Pydantic[pydantic 2.9+]
    Wikipedia[wikipedia-api]
    DuckDuckGo[duckduckgo-search]
    PyTZ[pytz]

    Pytest[pytest 8.3+]
    Ruff[ruff 0.6+]
    Mypy[mypy 1.11+]
    Cov[pytest-cov]

    SRC --> Aiogram
    SRC --> OpenAI
    SRC --> Pydantic
    SRC --> Wikipedia
    SRC --> DuckDuckGo
    SRC --> PyTZ

    Pytest -.test.-> SRC
    Ruff -.lint.-> SRC
    Mypy -.type.-> SRC
    Cov -.test.-> SRC

    style SRC fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Aiogram fill:#2196F3,stroke:#1565C0,color:#fff
    style OpenAI fill:#2196F3,stroke:#1565C0,color:#fff
    style Pydantic fill:#2196F3,stroke:#1565C0,color:#fff
    style Pytest fill:#FF9800,stroke:#E65100,color:#fff
    style Ruff fill:#FF9800,stroke:#E65100,color:#fff
    style Mypy fill:#FF9800,stroke:#E65100,color:#fff
```

---

## 🎯 Project Metrics

### Ключевые метрики проекта

| Категория | Метрика | Значение |
|-----------|---------|----------|
| **Code** | Модулей | 14 |
| **Code** | Строк кода | ~2000 |
| **Code** | Файлов | 23 |
| **Tests** | Тестов | 55 |
| **Tests** | Coverage | 78% |
| **Tests** | Failed | 0 |
| **Quality** | ruff | ✅ Pass |
| **Quality** | mypy | ✅ Pass |
| **Progress** | MVP | 7/9 iterations |
| **Progress** | TechDebt | 6/6 done |

---

## 📊 Architecture Patterns

### Используемые паттерны

| Паттерн | Где используется | Зачем |
|---------|------------------|-------|
| **Facade** | LLMClient | Упрощение работы с LLM |
| **Protocol** | Tool interface | Расширяемость tools |
| **Dependency Injection** | Config → все | Явные зависимости |
| **Repository** | ContextManager | Управление данными |
| **Strategy** | Tools | Разные стратегии поиска |

---

## 📚 Легенда цветов

| Цвет | Hex | Использование |
|------|-----|---------------|
| 🟢 Зеленый | #4CAF50 | Users, Success, Good |
| 🔵 Синий | #2196F3 | Core components |
| 🟣 Фиолетовый | #9C27B0 | Storage, State |
| 🟠 Оранжевый | #FF9800 | Handlers, Dev tools |
| 🔴 Красный | #F44336 | LLM, Critical, Bad |
| 🔴 Розовый | #E91E63 | Orchestration |
| 🔵 Голубой | #00BCD4 | Configuration |
| ⚫ Черный | #000000 | Wikipedia |
| 🟤 Коричневый | #de5833 | DuckDuckGo |

---

## 🔗 Связанные гайды

- **Architecture Overview:** [02_architecture_overview.md](02_architecture_overview.md)
- **Data Model:** [03_data_model.md](03_data_model.md)
- **Integrations:** [04_integrations.md](04_integrations.md)
- **Codebase Tour:** [05_codebase_tour.md](05_codebase_tour.md)
- **Development Workflow:** [07_development_workflow.md](07_development_workflow.md)

---

**Назначение диаграмм:**
- 📊 **Презентации** - показать архитектуру stakeholders
- 📝 **Документация** - визуализация технических решений
- 🎓 **Онбординг** - быстрое понимание системы
- 🔍 **Анализ** - поиск узких мест и возможностей рефакторинга
- 🗣️ **Коммуникация** - обсуждение архитектуры в команде
