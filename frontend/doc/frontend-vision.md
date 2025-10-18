# Техническое видение Frontend Dashboard

> Дата создания: 17 октября 2025
> Последнее обновление: 17 октября 2025
> Версия: 1.0
> Принцип: Modern, Type-safe, Accessible UI для LLM-ассистента

---

## 1. Технологии

### Основной стек

- **Next.js 15** - React framework с App Router для SSR/SSG
- **React 18** - библиотека для построения пользовательских интерфейсов
- **TypeScript 5** - статическая типизация для безопасности кода
- **Tailwind CSS 3** - utility-first CSS framework
- **shadcn/ui** - компонентная библиотека на базе Radix UI
- **pnpm** - быстрый и эффективный пакетный менеджер

### Дополнительные библиотеки

- **Recharts** - библиотека для визуализации данных (графики, диаграммы)
- **Radix UI** - примитивы доступных UI компонентов (через shadcn/ui)
- **clsx / tailwind-merge** - утилиты для работы с CSS классами
- **date-fns** - работа с датами (если потребуется)

### Инструменты разработки

- **ESLint** - линтер для JavaScript/TypeScript
- **Prettier** - форматтер кода
- **TypeScript Compiler** - проверка типов
- **Next.js Dev Server** - hot-reload для разработки

---

## 2. Принципы разработки

### Component-Driven Development

- **1 компонент = 1 файл = 1 ответственность**
- Композиция компонентов вместо наследования
- Переиспользуемые UI компоненты в `components/ui/`
- Бизнес-логика в custom hooks (`hooks/`)

### Type Safety First

- **TypeScript strict mode** включен всегда
- Type hints для всех props, state, функций
- Типы генерируются из API контракта
- Никакого `any` - только `unknown` если тип неизвестен
- `noUncheckedIndexedAccess` для безопасного доступа к массивам/объектам

### Accessibility First

- Семантический HTML
- ARIA атрибуты где необходимо
- Keyboard navigation support
- Screen reader friendly
- Color contrast compliance (WCAG 2.1 AA)

### Performance Optimization

- Server-side rendering (SSR) для начальной загрузки
- Client-side rendering для интерактивности
- Lazy loading компонентов где уместно
- Оптимизация изображений через Next.js Image
- Минимизация bundle size

### KISS (Keep It Simple, Stupid)

- Минимум абстракций и избыточных паттернов
- Прямолинейная логика без оверинжиниринга
- shadcn/ui вместо тяжелых UI библиотек
- Простые custom hooks вместо сложных state managers

### Явность (Explicit over Implicit)

- Явная передача props в компоненты
- Явные типы для всех данных
- Явная обработка ошибок и loading states

### Качество кода

- **Type hints** везде (TypeScript strict mode)
- **Короткие компоненты** максимум 150-200 строк
- **Понятные имена** компонентов и функций
- **Комментарии** на русском для сложной логики
- **ESLint + Prettier** для единообразия кода
- **No console.log** в production коде

---

## 3. Структура проекта

```
frontend/app/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # Root layout (темы, шрифты, providers)
│   │   ├── page.tsx              # Home page (redirect → /dashboard)
│   │   ├── dashboard/            # Dashboard routes
│   │   │   └── page.tsx          # Dashboard page
│   │   └── globals.css           # Global styles
│   │
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── table.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── select.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   └── chart.tsx
│   │   │
│   │   ├── layout/               # Layout components
│   │   │   ├── header.tsx        # App header with navigation
│   │   │   ├── sidebar.tsx       # Sidebar navigation (если нужен)
│   │   │   └── footer.tsx        # App footer
│   │   │
│   │   └── dashboard/            # Dashboard-specific components
│   │       ├── stats-cards.tsx   # 4 карточки с метриками
│   │       ├── activity-chart.tsx # График активности по времени
│   │       ├── recent-dialogs.tsx # Таблица последних диалогов
│   │       └── top-users.tsx     # Топ пользователей по активности
│   │
│   ├── lib/
│   │   ├── api.ts                # API client для Mock API
│   │   ├── types.ts              # TypeScript типы из API контракта
│   │   └── utils.ts              # Утилиты (cn, formatters и др.)
│   │
│   ├── hooks/                    # Custom React hooks
│   │   └── use-stats.ts          # Hook для получения статистики
│   │
│   └── styles/
│       └── globals.css           # Global styles + Tailwind imports
│
├── public/                       # Static assets
│   └── (images, icons, etc.)
│
├── components.json               # shadcn/ui configuration
├── next.config.js                # Next.js configuration
├── tailwind.config.ts            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
├── .eslintrc.json                # ESLint configuration
├── .prettierrc                   # Prettier configuration
├── .env.local                    # Environment variables (gitignored)
├── .env.example                  # Example env vars
├── package.json                  # Dependencies and scripts
├── pnpm-lock.yaml                # pnpm lock file
└── README.md                     # Project documentation
```

### Описание модулей

#### src/app/

Next.js App Router - файловая структура определяет маршруты:
- `layout.tsx` - общий layout для всего приложения
- `page.tsx` - главная страница (редирект на `/dashboard`)
- `dashboard/page.tsx` - страница dashboard со статистикой

#### src/components/ui/

shadcn/ui компоненты - переиспользуемые UI примитивы:
- Устанавливаются через CLI: `pnpm dlx shadcn@latest add <component>`
- Код компонентов находится в репозитории (не в node_modules)
- Можно кастомизировать под проект

#### src/components/layout/

Layout компоненты:
- `header.tsx` - шапка приложения с навигацией
- `footer.tsx` - подвал приложения

#### src/components/dashboard/

Dashboard-specific компоненты:
- `stats-cards.tsx` - 4 карточки с ключевыми метриками
- `activity-chart.tsx` - график активности (Recharts)
- `recent-dialogs.tsx` - таблица последних 10 диалогов
- `top-users.tsx` - топ-5 пользователей

#### src/lib/

Утилиты и API клиенты:
- `api.ts` - функции для запросов к Mock API
- `types.ts` - TypeScript типы из API контракта
- `utils.ts` - helper функции (cn, форматирование дат и т.д.)

#### src/hooks/

Custom React hooks:
- `use-stats.ts` - hook для получения статистики с обработкой loading/error

---

## 4. Архитектура приложения

### Схема взаимодействия

```
Browser
    ↓
[Next.js App Router]
    ↓
[Layout] - header, footer, theme provider
    ↓
[Dashboard Page]
    ↓ ↑
[useStats hook] ← fetch data
    ↓
[API Client] → Mock API (http://localhost:8000)
    ↓
[Dashboard Components]
    ├── StatsCards (4 карточки)
    ├── ActivityChart (график)
    ├── RecentDialogs (таблица)
    └── TopUsers (топ-5)
```

### Data Flow

1. **Загрузка данных:**
   - Dashboard page использует `useStats` hook
   - Hook вызывает API client (`lib/api.ts`)
   - API client делает fetch запрос к Mock API
   - Данные валидируются TypeScript типами

2. **Обработка состояний:**
   - Loading state - скелетоны/спиннеры
   - Error state - сообщение об ошибке
   - Success state - отображение данных

3. **Рендеринг компонентов:**
   - Dashboard передает данные в child компоненты
   - Компоненты рендерят UI с помощью shadcn/ui
   - Recharts рендерит графики

---

## 5. API Integration

### Mock API (FE-S1)

**Base URL:** `http://localhost:8000`

**Endpoints:**
- `GET /health` - health check
- `GET /api/v1/stats?period=day|week|month` - статистика

**Response Format:**
```typescript
interface StatsResponse {
  period: "day" | "week" | "month";
  generated_at: string; // ISO timestamp
  general_stats: GeneralStats;
  activity_chart: ActivityDataPoint[];
  recent_dialogs: DialogInfo[];
  top_users: UserActivity[];
}
```

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 6. Styling Strategy

### Tailwind CSS Utility-First

Используем Tailwind CSS для всех стилей:
- Utility classes вместо custom CSS
- Responsive design через Tailwind breakpoints
- Dark mode support через Tailwind (если потребуется)

### shadcn/ui Theming

- Цветовая схема: Slate (default)
- CSS Variables для кастомизации
- Файл: `src/app/globals.css`

### Responsive Design

Breakpoints (Tailwind defaults):
- `sm`: 640px (мобильные)
- `md`: 768px (планшеты)
- `lg`: 1024px (ноутбуки)
- `xl`: 1280px (десктопы)
- `2xl`: 1536px (большие экраны)

---

## 7. Testing Strategy

### Type Safety

- TypeScript compiler - первая линия защиты
- Strict mode включен
- No `any` types

### Linting

- ESLint для проверки кода
- Prettier для форматирования
- Pre-commit hooks (будут добавлены позже)

### Manual Testing

- Development server с hot-reload
- Тестирование в разных браузерах
- Responsive design testing

---

## 8. Development Workflow

### Commands

```bash
# Установка зависимостей
pnpm install

# Запуск dev сервера
pnpm dev

# Сборка production
pnpm build

# Проверка типов
pnpm type-check

# Линтинг
pnpm lint

# Форматирование
pnpm format
```

### Git Workflow

- Feature branches для новых фич
- Pull requests для code review
- Commit messages на английском

---

## 9. Architecture Decision Records (ADR)

Ключевые архитектурные решения документируются в ADR:

1. [ADR-001: Выбор Next.js](adr/001-nextjs-choice.md)
2. [ADR-002: Выбор shadcn/ui](adr/002-shadcn-ui-choice.md)
3. [ADR-003: Выбор pnpm](adr/003-pnpm-choice.md)

---

## 10. Roadmap

### FE-S2: Каркас frontend проекта (текущий спринт)

- ✅ Техническое видение и ADR
- ⏳ Инициализация Next.js проекта
- ⏳ Установка shadcn/ui
- ⏳ Создание структуры проекта
- ⏳ Настройка инструментов качества

### FE-S3: Dashboard со статистикой (следующий)

- Реализация dashboard компонентов
- Интеграция с Mock API
- Responsive design
- Тестирование

### FE-S4: ИИ-чат для администратора

- UI для чата
- Интеграция с chat API
- Text-to-SQL механизм

### FE-S5: Real API и интеграция с БД

- Переход на Real API
- Интеграция с PostgreSQL

---

## 11. Соглашения о коде

### Naming Conventions

- **Components:** PascalCase (`StatsCards`, `ActivityChart`)
- **Files:** kebab-case (`stats-cards.tsx`, `use-stats.ts`)
- **Functions:** camelCase (`fetchStats`, `formatDate`)
- **Constants:** UPPER_SNAKE_CASE (`API_BASE_URL`)
- **Types/Interfaces:** PascalCase (`StatsResponse`, `User`)

### Component Structure

```typescript
// 1. Imports
import { ReactNode } from "react";
import { Card } from "@/components/ui/card";

// 2. Types
interface StatsCardsProps {
  data: GeneralStats;
}

// 3. Component
export function StatsCards({ data }: StatsCardsProps): ReactNode {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Component content */}
    </div>
  );
}
```

### Import Organization

```typescript
// 1. React / Next.js imports
import { useState, useEffect } from "react";
import Link from "next/link";

// 2. External libraries
import { formatDate } from "date-fns";

// 3. Internal components
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// 4. Internal utilities
import { cn } from "@/lib/utils";
import { fetchStats } from "@/lib/api";

// 5. Types
import type { StatsResponse } from "@/lib/types";
```

---

## 12. Ограничения и компромиссы

### Что НЕ делаем в MVP

- ❌ Server-side authentication (пока нет auth)
- ❌ Real-time updates (WebSockets) - только polling при необходимости
- ❌ Сложные state managers (Redux, Zustand) - React Context достаточно
- ❌ Анимации и transitions (будут добавлены позже)
- ❌ Мультиязычность (i18n) - только русский язык
- ❌ Unit/E2E тесты (будут добавлены позже)

### Технический долг

- TODO: добавить pre-commit hooks
- TODO: добавить E2E тесты (Playwright)
- TODO: добавить Storybook для компонентов
- TODO: оптимизация bundle size

---

**Версия:** 1.0
**Дата:** 2025-10-17
**Статус:** Активный документ

