# 📚 Навигация по документации проекта

> **systech-aidd_mcr** - LLM Assistant Telegram Bot
> Последнее обновление: 16 октября 2025

---

## 🎯 Быстрый старт по ролям

### 👨‍💻 Новый разработчик (День 1)
```
1. 📖 01_getting_started.md       ← Запустить проект (15 мин)
2. 🗺️  05_codebase_tour.md        ← Понять структуру (20 мин)
3. ⚙️  06_configuration.md        ← Научиться настраивать (10 мин)
4. 🔄 07_development_workflow.md  ← Как работать (15 мин)
```

### 🏗️ Middle/Senior разработчик (День 1)
```
1. 📖 01_getting_started.md       ← Быстрый старт (10 мин)
2. 🎨 11_visual_architecture.md   ← Визуализации (20 мин)
3. 🏛️  02_architecture_overview.md ← Архитектура (20 мин)
4. 📊 03_data_model.md            ← Модели данных (15 мин)
5. 🔌 04_integrations.md          ← Интеграции (20 мин)
```

### 🚀 Senior/Tech Lead (День 1)
```
1. 🎨 11_visual_architecture.md   ← Визуализация системы (20 мин)
2. 🏛️  02_architecture_overview.md ← Архитектурные решения (20 мин)
3. 🔌 04_integrations.md          ← Внешние интеграции (20 мин)
4. 🔄 07_development_workflow.md  ← Процессы и code review (20 мин)
5. 🐳 09_deployment.md            ← Деплой стратегия (15 мин)
```

### 🚀 DevOps инженер
```
1. 📖 01_getting_started.md       ← Что это такое (10 мин)
2. ⚙️  06_configuration.md        ← Конфигурация (15 мин)
3. 🐳 09_deployment.md            ← Деплой (20 мин)
4. 🔧 10_troubleshooting.md       ← Проблемы (справочник)
```

---

## 📖 Все гайды по порядку

| # | Гайд | Время | Описание |
|---|------|-------|----------|
| 00 | **README** (этот файл) | 5 мин | Навигация по документации |
| 01 | [Getting Started](01_getting_started.md) | 15 мин | Быстрый старт с нуля |
| 02 | [Architecture Overview](02_architecture_overview.md) | 20 мин | Обзор архитектуры |
| 03 | [Data Model](03_data_model.md) | 15 мин | Модель данных (Pydantic) |
| 04 | [Integrations](04_integrations.md) | 20 мин | Внешние интеграции |
| 05 | [Codebase Tour](05_codebase_tour.md) | 30 мин | Тур по репозиторию |
| 06 | [Configuration](06_configuration.md) | 15 мин | Конфигурация и секреты |
| 07 | [Development Workflow](07_development_workflow.md) | 20 мин | Процессы разработки |
| 08 | [Testing Guide](08_testing_guide.md) | 25 мин | Тестирование и QA |
| 09 | [Deployment](09_deployment.md) | 15 мин | Запуск и деплой |
| 10 | [Troubleshooting](10_troubleshooting.md) | - | Решение проблем (FAQ) |
| 11 | [Visual Architecture](11_visual_architecture.md) | 20 мин | Визуализации и диаграммы |

**Общее время:** ~3.5 часа для полного изучения

---

## 📚 Основная техническая документация

### Обязательно к прочтению
- **[vision.md](../vision.md)** - полное техническое видение проекта (2000+ строк)
- **[conventions.md](../conventions.md)** - правила разработки (KISS, SOLID, DRY)

### Планирование
- **[roadmap.md](../roadmap.md)** - роадмап проекта по спринтам
- **[tasklist-s0.md](../tasklists/tasklist-s0.md)** - план разработки MVP спринта S0 (итерации 1-7)
- **[tasklist-techdebt-s0.md](../tasklists/tasklist-techdebt-s0.md)** - рефакторинг спринта S0 (итерации 1-6)

### Концепция
- **[idea.md](../idea.md)** - концепция проекта (роли, ИИ-продукт)

---

## 🔍 Поиск информации

### Я хочу узнать...

**...как запустить проект**
→ [01_getting_started.md](01_getting_started.md)

**...как устроена архитектура**
→ [02_architecture_overview.md](02_architecture_overview.md)

**...где находится конкретный функционал**
→ [05_codebase_tour.md](05_codebase_tour.md)

**...как работают Pydantic модели**
→ [03_data_model.md](03_data_model.md)

**...как интегрированы Telegram/OpenAI/Wikipedia**
→ [04_integrations.md](04_integrations.md)

**...где настраиваются параметры и роль бота**
→ [06_configuration.md](06_configuration.md)

**...как писать и коммитить код**
→ [07_development_workflow.md](07_development_workflow.md)

**...как писать тесты**
→ [08_testing_guide.md](08_testing_guide.md)

**...как деплоить проект**
→ [09_deployment.md](09_deployment.md)

**...почему что-то не работает**
→ [10_troubleshooting.md](10_troubleshooting.md)

**...увидеть визуализацию архитектуры**
→ [11_visual_architecture.md](11_visual_architecture.md)

---

## 🎓 Глоссарий

| Термин | Описание |
|--------|----------|
| **LLM** | Large Language Model (OpenAI GPT) |
| **Tool** | Инструмент для LLM (Wikipedia, WebSearch, DateTime) |
| **Function Calling** | Механизм вызова tools через OpenAI API |
| **Context** | История диалога пользователя (in-memory) |
| **Role** | Роль бота (определяется системным промптом) |
| **System Prompt** | Инструкция для LLM (загружается из файла) |
| **Handler** | Обработчик команд/сообщений Telegram |
| **Orchestrator** | Компонент для управления tool calling loop |
| **Protocol** | Интерфейс для tools (typing.Protocol) |
| **uv** | Менеджер зависимостей Python (замена pip) |

---

## 📊 Статус проекта

```
MVP:        7/9 итераций завершено (78%)
TechDebt:   6/6 итераций завершено (100%)
Tests:      55 passed, 0 failed
Coverage:   78%
Линтеры:    ruff ✅, mypy ✅
```

---

## 🆘 Нужна помощь?

1. **Проверь FAQ:** [10_troubleshooting.md](10_troubleshooting.md)
2. **Поищи в документации:** Используй Ctrl+F в vision.md
3. **Изучи код:** [05_codebase_tour.md](05_codebase_tour.md) подскажет где что

---

**Приятного изучения! 🚀**

