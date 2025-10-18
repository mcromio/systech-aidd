# 🎨 Visual Architecture - Визуальная архитектура (ASCII версия)

> Визуализация для терминалов и текстовых редакторов

---

## 📋 Содержание

1. [High-Level Architecture](#1-high-level-architecture)
2. [Component Structure](#2-component-structure)
3. [Data Flow](#3-data-flow)
4. [Module Dependencies](#4-module-dependencies)
5. [State Management](#5-state-management)
6. [Message Processing](#6-message-processing)

---

## 1️⃣ High-Level Architecture

### Общая архитектура системы

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │  User 1  │  │  User 2  │  │  User N  │                      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
└───────┼─────────────┼─────────────┼────────────────────────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
        ┌─────────────▼──────────────────┐
        │   TELEGRAM BOT API              │
        └─────────────┬──────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────────┐
│                  APPLICATION LAYER                              │
│                                                                 │
│  ┌──────────────┐     ┌─────────────────┐                     │
│  │ TelegramBot  │────▶│ MessageHandler  │                     │
│  └──────────────┘     └────────┬────────┘                     │
│                                 │                               │
│              ┌──────────────────┼──────────────────┐           │
│              │                  │                  │           │
│              ▼                  ▼                  ▼           │
│    ┌──────────────┐   ┌──────────────┐  ┌──────────────┐     │
│    │   Context    │   │   LLMClient  │  │    Config    │     │
│    │   Manager    │   └──────┬───────┘  └──────────────┘     │
│    └──────────────┘          │                                │
│                               │                                │
│                    ┌──────────┴──────────┐                    │
│                    ▼                     ▼                    │
│          ┌──────────────┐      ┌──────────────┐              │
│          │ OpenAIClient │      │Orchestrator  │              │
│          └──────┬───────┘      └──────┬───────┘              │
│                 │                     │                       │
│                 └──────────┬──────────┘                       │
│                            │                                  │
│                    ┌───────┴───────┐                         │
│                    │     TOOLS     │                         │
│         ┌──────────┼───────────────┼──────────┐              │
│         ▼          ▼               ▼          ▼              │
│    ┌────────┐ ┌────────┐     ┌──────────┐                   │
│    │  Wiki  │ │DateTime│     │WebSearch │                   │
│    └────┬───┘ └────────┘     └────┬─────┘                   │
└─────────┼──────────────────────────┼────────────────────────┘
          │                          │
┌─────────▼──────────────────────────▼────────────────────────┐
│                  EXTERNAL SERVICES                           │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  OpenAI    │  │ Wikipedia  │  │ DuckDuckGo │           │
│  │    API     │  │    API     │  │            │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ Component Structure

### Структура модулей

```
src/
│
├─ main.py ──────────┐
│                    │
├─ config.py ◄───────┤
│      │             │
│      ▼             │
│  [Configuration]   │
│                    │
├─ bot.py ◄──────────┤
│      │             │
│      ▼             │
├─ handlers.py ◄─────┤
│      │             │
│      ▼             │
├─ context_manager.py ◄──┘
│
├─ llm_client.py ────┐
│      │             │
│      ▼             │
├─ llm/              │
│   ├─ client.py ◄───┤
│   └─ orchestrator.py ◄──┘
│
└─ tools/
    ├─ base.py (Protocol)
    │      ▲
    │      │
    ├─ wikipedia.py (implements Tool)
    ├─ datetime.py (implements Tool)
    └─ websearch.py (implements Tool)
```

---

## 3️⃣ Data Flow

### Поток обработки сообщения

```
1. USER
   │
   ▼
2. TELEGRAM API
   │
   ▼
3. TelegramBot
   │
   ▼
4. MessageHandler
   │
   ├─────────────────────┐
   │                     │
   ▼                     ▼
5. ContextManager     6. LLMClient
   │                     │
   │ add_message(user)   ▼
   │ get_history()    7. ToolOrchestrator
   │                     │
   │                     ├─────────────┐
   │                     │             │
   │                     ▼             ▼
   │                  8. OpenAI     9. Tools
   │                     │             │
   │                     │ ◄───────────┘
   │                     │
   │                     ▼
   │                  10. Response
   │                     │
   ◄─────────────────────┘
   │
   │ add_message(assistant)
   │
   ▼
11. MessageHandler
   │
   ▼
12. TelegramBot
   │
   ▼
13. TELEGRAM API
   │
   ▼
14. USER (получает ответ)
```

---

## 4️⃣ Module Dependencies

### Зависимости проекта

```
APPLICATION (src/)
│
├─ Runtime Dependencies:
│  ├─ aiogram 3.13+          [Telegram Bot]
│  ├─ openai 1.51+           [LLM API]
│  ├─ pydantic 2.9+          [Validation]
│  ├─ wikipedia-api 0.7+     [Wikipedia]
│  ├─ duckduckgo-search 8.1+ [Web Search]
│  └─ pytz 2025.2+           [Timezones]
│
└─ Development Dependencies:
   ├─ pytest 8.3+            [Testing]
   ├─ pytest-asyncio 0.24+   [Async Tests]
   ├─ pytest-cov 5.0+        [Coverage]
   ├─ ruff 0.6+              [Linter]
   └─ mypy 1.11+             [Type Checker]
```

---

## 5️⃣ State Management

### Жизненный цикл контекста

```
┌─────────────────────────────────────────────────┐
│  NEW USER                                        │
│  (first message)                                 │
│         │                                        │
│         ▼                                        │
│  ┌────────────────┐                             │
│  │ Create Context │                             │
│  └────────┬───────┘                             │
│           │                                      │
│           ▼                                      │
│  ┌─────────────────────────────────────────┐   │
│  │    ACTIVE DIALOG                         │   │
│  │                                          │   │
│  │  ┌──────────────────┐                   │   │
│  │  │ Receive Message  │                   │   │
│  │  └────────┬─────────┘                   │   │
│  │           │                              │   │
│  │           ▼                              │   │
│  │  ┌──────────────────┐                   │   │
│  │  │ Process with LLM │                   │   │
│  │  └────────┬─────────┘                   │   │
│  │           │                              │   │
│  │           ▼                              │   │
│  │  ┌──────────────────┐                   │   │
│  │  │ Store Response   │                   │   │
│  │  └────────┬─────────┘                   │   │
│  │           │                              │   │
│  │           └──────┐                       │   │
│  │                  │                       │   │
│  └──────────────────┼───────────────────────┘   │
│                     │                            │
│           ┌─────────┴──────────┐                │
│           │                    │                │
│           ▼                    ▼                │
│    messages > MAX?      /reset command?        │
│           │                    │                │
│           ▼                    ▼                │
│    ┌────────────┐      ┌────────────┐          │
│    │ Trim Old   │      │   Clear    │          │
│    └─────┬──────┘      └─────┬──────┘          │
│          │                   │                  │
│          └─────────┬─────────┘                  │
│                    │                            │
│                    ▼                            │
│             Back to Active                      │
│                                                 │
│  Bot Restart ────► [Context Lost]              │
└─────────────────────────────────────────────────┘
```

---

## 6️⃣ Message Processing

### Tool Calling Loop

```
┌────────────────────────────────────────────────┐
│ ORCHESTRATOR                                    │
│                                                 │
│  messages = [system_prompt + user_messages]    │
│  iteration = 0                                  │
│  max_iterations = 10                            │
│                                                 │
│  LOOP (while iteration < max_iterations):      │
│    │                                            │
│    ├─► Call OpenAI API                         │
│    │       │                                    │
│    │       ▼                                    │
│    │   Get Response                             │
│    │       │                                    │
│    │       ├─► Has tool_calls?                 │
│    │       │      │                             │
│    │       │      ├─ NO ──► Return response ✓  │
│    │       │      │                             │
│    │       │      └─ YES                        │
│    │       │          │                         │
│    │       │          ▼                         │
│    │       │   ┌──────────────┐                │
│    │       │   │ Execute Tool │                │
│    │       │   └──────┬───────┘                │
│    │       │          │                         │
│    │       │          ▼                         │
│    │       │   Add result to messages           │
│    │       │          │                         │
│    │       └──────────┘                         │
│    │                                            │
│    └─► iteration++                              │
│                                                 │
│  IF iteration >= max_iterations:                │
│     Return "Limit exceeded" ⚠                  │
│                                                 │
└────────────────────────────────────────────────┘
```

---

## 📊 Test Coverage

### Покрытие по модулям

```
MODULE                    COVERAGE    STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
context_manager.py        100% ████████████ ✅
llm_client.py             100% ████████████ ✅
config.py                  96% ███████████▌ ✅
handlers.py                93% ███████████▏ ✅
wikipedia.py               92% ███████████  ✅
orchestrator.py            87% ██████████▍  ✅
websearch.py               83% █████████▉   ✅
datetime.py                82% █████████▊   ✅
client.py                  72% ████████▋    ⚠️
bot.py                      0%              ❌
main.py                     0%              ❌
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL                      78% █████████▍   ✅
```

---

## 📈 Project Metrics

```
┌─────────────────────────────────────────┐
│          PROJECT METRICS                 │
├─────────────────────────────────────────┤
│                                         │
│  Code:                                  │
│    • Modules:      14                   │
│    • Lines:        ~2000                │
│    • Files:        23                   │
│                                         │
│  Tests:                                 │
│    • Total:        55                   │
│    • Passed:       55 ✅                │
│    • Failed:       0                    │
│    • Coverage:     78%                  │
│                                         │
│  Quality:                               │
│    • ruff:         ✅ Pass              │
│    • mypy:         ✅ Pass              │
│    • Type hints:   ✅ Everywhere        │
│                                         │
│  Progress:                              │
│    • MVP:          7/9 iterations       │
│    • TechDebt:     6/6 completed        │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔧 Commands Flow

### Обработка команд

```
INCOMING MESSAGE
      │
      ▼
┌──────────┐
│  /start  │──► Show welcome message
└──────────┘

┌──────────┐
│  /help   │──► Show help text
└──────────┘

┌──────────┐
│  /role   │──► Show bot role info
└──────────┘         │
                     ▼
              ┌──────────────┐
              │ Role Name:   │
              │ Description: │
              │ Prompt file: │
              └──────────────┘

┌──────────┐
│  /reset  │──► Clear user context
└──────────┘         │
                     ▼
              ┌──────────────┐
              │ Clear history│
              │ for user_id  │
              └──────────────┘

┌──────────┐
│   text   │──► Process with LLM
└──────────┘         │
                     ▼
              ┌──────────────┐
              │ Add to ctx   │
              │ Call LLM     │
              │ Get response │
              │ Add to ctx   │
              │ Send to user │
              └──────────────┘
```

---

## 🎯 Architecture Patterns

```
┌────────────────────────────────────────────┐
│  PATTERN          │  WHERE         │ WHY   │
├────────────────────────────────────────────┤
│  Facade           │  LLMClient     │ Hide  │
│                   │                │ complex│
│                                            │
│  Protocol         │  Tool          │ Open/ │
│                   │                │ Closed│
│                                            │
│  Dependency       │  Config →      │ Testable│
│  Injection        │  everywhere    │       │
│                                            │
│  Repository       │  ContextMgr    │ Data  │
│                   │                │ access│
│                                            │
│  Strategy         │  Tools         │ Runtime│
│                   │                │ choice│
└────────────────────────────────────────────┘
```

---

## 🔗 Связанные гайды

- **Mermaid версия:** [11_visual_architecture.md](11_visual_architecture.md)
- **Architecture Overview:** [02_architecture_overview.md](02_architecture_overview.md)
- **Codebase Tour:** [05_codebase_tour.md](05_codebase_tour.md)

---

**💡 Совет:** Для полноценных диаграмм используйте Mermaid версию этого документа с расширением для VS Code или на GitHub.






