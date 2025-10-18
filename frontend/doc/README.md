# Frontend Documentation

> **Документация пользовательского интерфейса проекта**

---

## 📋 Содержание

- [frontend-roadmap.md](frontend-roadmap.md) - стратегический план развития frontend
- [frontend-vision.md](frontend-vision.md) - техническое видение UI (✅ создано в FE-S2)
- [api-contract.md](api-contract.md) - контракт Mock Stats API
- [api-usage.md](api-usage.md) - примеры использования API
- [dashboard-requirements.md](dashboard-requirements.md) - требования к dashboard UI
- [plans/](plans/) - детальные планы спринтов
- [adr/](adr/) - Architecture Decision Records

---

## 📖 Основные документы

### 1. Frontend Roadmap
**Файл:** [frontend-roadmap.md](frontend-roadmap.md)

Стратегический план развития пользовательского интерфейса с таблицей спринтов и их описанием.

**Спринты:**
- **FE-S1:** ✅ Mock API для статистики диалогов
- **FE-S2:** ✅ Каркас frontend проекта
- **FE-S3:** 💡 Dashboard со статистикой
- **FE-S4:** 💡 ИИ-чат для администратора
- **FE-S5:** 💡 Real API и интеграция с БД

### 2. Frontend Vision
**Файл:** [frontend-vision.md](frontend-vision.md) ✅ **Завершен в FE-S2**

Техническое видение frontend части проекта:
- Технологический стек (Next.js 15, React 19, TypeScript, Tailwind CSS)
- Архитектурные решения и принципы
- Структура проекта
- Соглашения о коде

### 3. Architecture Decision Records (ADR)
**Директория:** [adr/](adr/) ✅ **Завершены в FE-S2**

- [001-nextjs-choice.md](adr/001-nextjs-choice.md) - Выбор Next.js
- [002-shadcn-ui-choice.md](adr/002-shadcn-ui-choice.md) - Выбор shadcn/ui
- [003-pnpm-choice.md](adr/003-pnpm-choice.md) - Выбор pnpm

### 4. API Documentation
**Файлы:**
- [api-contract.md](api-contract.md) - Полный контракт API
- [api-usage.md](api-usage.md) - Примеры использования для разных платформ
- [dashboard-requirements.md](dashboard-requirements.md) - Требования к dashboard UI

### 5. Sprint Plans
**Директория:** [plans/](plans/)

Детальные планы выполнения каждого спринта с разбивкой на итерации.

**Доступные планы:**
- [plans/s2-init-plan.md](plans/s2-init-plan.md) - ✅ План FE-S2 (завершен)

---

## 🚀 Быстрый старт

### Для начала работы над Frontend

1. **Изучите стратегию:**
   ```bash
   cat frontend/doc/frontend-roadmap.md
   cat frontend/doc/frontend-vision.md
   ```

2. **Запустите frontend dev сервер:**
   ```bash
   make fe-dev
   ```
   Доступен на [http://localhost:3000](http://localhost:3000)

3. **Запустите Mock API (если не запущен):**
   ```bash
   make api-run
   ```
   API доступен на [http://localhost:8000](http://localhost:8000)

4. **Проверьте качество кода:**
   ```bash
   make fe-quality
   ```

### Структура проекта

Frontend приложение находится в `frontend/app/`:

```
frontend/app/
├── src/
│   ├── app/              # Next.js App Router
│   ├── components/       # React компоненты
│   ├── lib/              # Утилиты и типы
│   ├── hooks/            # Custom React hooks
│   └── styles/           # Стили
├── package.json          # Зависимости (pnpm)
└── README.md             # Документация приложения
```

Детальная документация: [frontend/app/README.md](../app/README.md)

---

## 🎯 Цели Frontend проекта

### Dashboard со статистикой
- Визуализация метрик диалогов и пользователей
- Графики активности (Recharts)
- Таблицы данных и топ-пользователи
- Адаптивный дизайн (responsive)
- Интеграция с Mock API

### ИИ-чат для администратора (FE-S4)
- Веб-интерфейс для общения с ИИ-ассистентом
- Text-to-SQL для аналитических запросов
- Получение ответов на вопросы по статистике

---

## 📚 Связанные документы

### Backend проекта
- [../../docs/roadmap.md](../../docs/roadmap.md) - roadmap backend
- [../../docs/vision.md](../../docs/vision.md) - техническое видение backend
- [../../docs/conventions.md](../../docs/conventions.md) - соглашения о коде

### Методология
- [../../docs/roadmap_templates/README.md](../../docs/roadmap_templates/README.md) - шаблоны планирования

---

## 🔄 Workflow разработки

```
1. Roadmap (frontend-roadmap.md)
   ↓ Выбрать спринт

2. Plan Mode (plans/fe-sN-plan.md)
   ↓ Детальное планирование (опционально)

3. Разработка
   ↓ Выполнение итераций

4. Тестирование
   ↓ Проверка качества (make fe-quality)

5. Интеграция
   ↓ Связывание с backend

6. Обновление roadmap
   ↓ Добавить статус ✅ и ссылку на план
```

---

## 📊 Техстек FE-S2

### Framework & Language
- **Next.js 15** - React framework с App Router
- **React 19** - UI библиотека
- **TypeScript 5** - Статическая типизация (strict mode)

### Styling
- **Tailwind CSS 3** - Utility-first CSS framework
- **Radix UI** - Доступные UI примитивы

### Libraries
- **Recharts** - Визуализация данных (графики)
- **clsx** - Утилиты для CSS классов

### Package Manager
- **pnpm 10+** - Быстрый и эффективный пакетный менеджер

### Development Tools
- **ESLint** - Линтер для качества кода
- **Prettier** - Форматтер кода
- **TypeScript Compiler** - Проверка типов

---

## 🛠️ Makefile Команды

### Installation
```bash
make fe-install      # Установить зависимости
```

### Development
```bash
make fe-dev          # Запустить dev сервер (http://localhost:3000)
make fe-build        # Собрать для production
make fe-start        # Запустить production сервер
```

### Code Quality
```bash
make fe-lint         # Запустить ESLint
make fe-format       # Форматировать код (Prettier)
make fe-type-check   # Проверить TypeScript типы
make fe-quality      # Все проверки качества
```

---

## 📈 FE-S2 (Итерации 1-6)

### ✅ Iteration 1: Technical Vision & ADR
- [x] frontend-vision.md
- [x] ADR-001: Next.js choice
- [x] ADR-002: shadcn/ui choice
- [x] ADR-003: pnpm choice

### ✅ Iteration 2: Next.js Project Init
- [x] TypeScript strict mode + extra parameters
- [x] App Router с src-dir
- [x] Alias @/*
- [x] Scripts: dev, build, lint, format, type-check

### ✅ Iteration 3: Dependencies & Structure
- [x] Radix UI + Recharts установлены
- [x] Структура директорий создана
- [x] TypeScript типы из API контракта

### ✅ Iteration 4: Components & Hooks
- [x] API client для Mock API
- [x] Custom hook useStats
- [x] Layout компоненты (Header, Footer)
- [x] Dashboard компоненты (StatsCards, ActivityChart, RecentDialogs, TopUsers)
- [x] Dashboard page с интеграцией

### ✅ Iteration 5: Quality Tools
- [x] Prettier конфигурация
- [x] ESLint настройка
- [x] TypeScript strict mode проверка

### ✅ Iteration 6: Documentation & Commands
- [x] Makefile frontend команды
- [x] frontend/app/README.md
- [x] Frontend roadmap обновлен
- [x] Этот README обновлен

---

## 📌 Status

**FE-S2:** ✅ **ЗАВЕРШЕН**

- Проект инициализирован и готов к использованию
- Dev сервер запускается без ошибок
- TypeScript проверка проходит
- Все компоненты созданы и типизированы
- Готово для FE-S3: Dashboard Implementation

---

**Версия:** 2.0
**Дата:** 2025-10-17
**Статус:** ✅ Завершено

*Начните с [frontend-roadmap.md](frontend-roadmap.md) для понимания общего плана развития!*

