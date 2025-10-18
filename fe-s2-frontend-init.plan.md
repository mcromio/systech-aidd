<!-- 2d4090c2-04ad-4dcf-8a3b-ebc1bc8fe3a0 4efd0312-ea52-4acc-b820-348e8acef41b -->
# Sprint Plan: FE-S2 - Инициализация Frontend проекта

## Цели спринта

1. Создать техническое видение frontend части проекта (frontend-vision.md)
2. Инициализировать Next.js проект с TypeScript и pnpm
3. Настроить shadcn/ui компоненты и Tailwind CSS
4. Создать структуру директорий и базовые компоненты
5. Настроить инструменты разработки (ESLint, Prettier, TypeScript)
6. Добавить команды для frontend в Makefile

## Технологический стек

- **Framework:** Next.js 15 (App Router)
- **Язык:** TypeScript 5
- **UI Library:** shadcn/ui
- **Styling:** Tailwind CSS 3
- **Пакетный менеджер:** pnpm
- **Качество кода:** ESLint, Prettier, TypeScript strict mode

## Итерации

### Iteration 1: Техническое видение и ADR (0.5 дня)

**Цель:** Создать документ frontend-vision.md и Architecture Decision Records

**Задачи:**

- Создать `frontend/doc/frontend-vision.md` по аналогии с `docs/vision.md`
- Документировать выбранный технологический стек
- Определить принципы разработки frontend:
  - Component-driven development
  - Type safety (TypeScript strict mode)
  - Accessibility first
  - Performance optimization
- Создать ADR документы в `frontend/doc/adr/`:
  - `001-nextjs-choice.md` - выбор Next.js
  - `002-shadcn-ui-choice.md` - выбор shadcn/ui
  - `003-pnpm-choice.md` - выбор pnpm как пакетного менеджера
- Определить структуру директорий проекта

**Критерий готовности:**

```bash
cat frontend/doc/frontend-vision.md
# Содержит: техстек, принципы, структуру проекта

ls frontend/doc/adr/
# 001-nextjs-choice.md
# 002-shadcn-ui-choice.md
# 003-pnpm-choice.md
```

---

### Iteration 2: Инициализация Next.js проекта (0.5 дня)

**Цель:** Создать Next.js проект с TypeScript и базовой конфигурацией

**Задачи:**

- Установить pnpm глобально (если не установлен)
- Создать Next.js проект в `frontend/app/`:
  ```bash
  cd frontend
  pnpm create next-app@latest app --typescript --tailwind --app --src-dir --import-alias "@/*"
  ```
- Настроить TypeScript с strict mode в `tsconfig.json`
- Настроить `next.config.js`:
  - Добавить API proxy для Mock API (http://localhost:8000)
  - Настроить переменные окружения
- Создать `.env.local` с настройками:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```
- Проверить работоспособность dev сервера

**Критерий готовности:**

```bash
cd frontend/app
pnpm dev
# Dev сервер запущен на http://localhost:3000

curl http://localhost:3000
# Главная страница Next.js работает
```

---

### Iteration 3: Установка и настройка shadcn/ui (0.5 дня)

**Цель:** Настроить shadcn/ui и установить необходимые компоненты

**Задачи:**

- Инициализировать shadcn/ui в проекте:
  ```bash
  pnpm dlx shadcn@latest init
  ```
- Выбрать стиль: Default
- Выбрать базовый цвет: Slate
- Настроить `components.json`
- Установить базовые компоненты для dashboard:
  ```bash
  pnpm dlx shadcn@latest add button card
  pnpm dlx shadcn@latest add table badge
  pnpm dlx shadcn@latest add select dropdown-menu
  pnpm dlx shadcn@latest add chart
  ```
- Создать файл `src/lib/utils.ts` (если не создан shadcn)
- Проверить что компоненты доступны

**Критерий готовности:**

```bash
ls frontend/app/src/components/ui/
# button.tsx card.tsx table.tsx badge.tsx
# select.tsx dropdown-menu.tsx chart.tsx

cat frontend/app/components.json
# Конфигурация shadcn/ui присутствует
```

---

### Iteration 4: Структура проекта и базовые компоненты (1 день)

**Цель:** Создать структуру директорий и базовые компоненты

**Задачи:**

- Создать структуру в `frontend/app/src/`:
  ```
  src/
  ├── app/                  # Next.js App Router
  │   ├── layout.tsx        # Root layout
  │   ├── page.tsx          # Home page (redirect to /dashboard)
  │   └── dashboard/        # Dashboard страница
  │       └── page.tsx
  ├── components/
  │   ├── ui/               # shadcn/ui компоненты
  │   ├── layout/           # Layout компоненты
  │   │   ├── header.tsx
  │   │   ├── sidebar.tsx
  │   │   └── footer.tsx
  │   └── dashboard/        # Dashboard компоненты
  │       ├── stats-cards.tsx
  │       ├── activity-chart.tsx
  │       ├── recent-dialogs.tsx
  │       └── top-users.tsx
  ├── lib/
  │   ├── api.ts            # API client для Mock API
  │   ├── types.ts          # TypeScript типы из API контракта
  │   └── utils.ts          # Утилиты
  ├── hooks/                # Custom React hooks
  │   └── use-stats.ts      # Hook для получения статистики
  └── styles/
      └── globals.css       # Глобальные стили
  ```
- Создать базовый Layout с Header и Footer
- Создать заглушки для dashboard компонентов
- Создать TypeScript типы на основе `frontend/doc/api-contract.md`

**Критерий готовности:**

```bash
tree frontend/app/src -L 2
# Структура директорий создана

cat frontend/app/src/lib/types.ts
# TypeScript типы StatsResponse, GeneralStats и др.

pnpm dev
# Приложение запускается без ошибок
```

---

### Iteration 5: Настройка инструментов качества (0.5 дня)

**Цель:** Настроить ESLint, Prettier и TypeScript для качества кода

**Задачи:**

- Настроить ESLint в `.eslintrc.json`:
  - Правила для React/Next.js
  - Правила для TypeScript
  - Правила для accessibility (eslint-plugin-jsx-a11y)
- Создать `.prettierrc`:
  ```json
  {
    "semi": true,
    "trailingComma": "es5",
    "singleQuote": false,
    "printWidth": 100,
    "tabWidth": 2
  }
  ```
- Создать `.prettierignore`
- Настроить TypeScript strict mode в `tsconfig.json`:
  ```json
  {
    "compilerOptions": {
      "strict": true,
      "noUncheckedIndexedAccess": true,
      "noImplicitReturns": true
    }
  }
  ```
- Добавить scripts в `package.json`:
  ```json
  {
    "scripts": {
      "lint": "next lint",
      "format": "prettier --write .",
      "type-check": "tsc --noEmit"
    }
  }
  ```

**Критерий готовности:**

```bash
cd frontend/app
pnpm lint
# ESLint проверка проходит

pnpm format
# Prettier форматирует код

pnpm type-check
# TypeScript проверка проходит без ошибок
```

---

### Iteration 6: Makefile команды и документация (0.5 дня)

**Цель:** Добавить команды для frontend в Makefile и создать документацию

**Задачи:**

- Добавить команды в корневой `Makefile`:
  ```makefile
  # Frontend команды
  fe-install:  ## Установить frontend зависимости
  fe-dev:      ## Запустить frontend dev сервер
  fe-build:    ## Собрать frontend для production
  fe-lint:     ## Проверить frontend код линтером
  fe-format:   ## Форматировать frontend код
  fe-test:     ## Запустить frontend тесты
  fe-type-check: ## Проверить TypeScript типы
  ```
- Создать `frontend/app/README.md` с инструкциями:
  - Как запустить проект
  - Структура проекта
  - Команды разработки
  - Соглашения о коде
- Добавить в `.gitignore`:
  ```
  frontend/app/.next/
  frontend/app/node_modules/
  frontend/app/.env*.local
  ```
- Создать `frontend/app/.env.example` с примерами переменных
- Обновить `frontend/doc/frontend-roadmap.md`:
  - Изменить статус FE-S2 на "Завершен"
  - Добавить ссылку на план

**Критерий готовности:**

```bash
make fe-dev
# Frontend запущен на http://localhost:3000

make fe-lint
# Линтер проходит

cat frontend/app/README.md
# Документация присутствует

cat frontend/doc/frontend-roadmap.md
# FE-S2 помечен как "Завершен" со ссылкой на план
```

---

## Definition of Done

Спринт считается завершенным, если:

1. ✅ Создан документ `frontend/doc/frontend-vision.md` с техническим видением
2. ✅ Созданы ADR документы для ключевых технических решений
3. ✅ Next.js проект инициализирован в `frontend/app/` с TypeScript
4. ✅ shadcn/ui установлен и настроен с базовыми компонентами
5. ✅ Создана структура директорий проекта
6. ✅ Созданы TypeScript типы на основе API контракта
7. ✅ Настроены ESLint, Prettier, TypeScript strict mode
8. ✅ Добавлены команды в Makefile для работы с frontend
9. ✅ Создана документация в `frontend/app/README.md`
10. ✅ Dev сервер запускается без ошибок на http://localhost:3000
11. ✅ Линтер и type-checker проходят без ошибок
12. ✅ Frontend roadmap обновлен со статусом спринта

---

## Проверка консистентности плана

### Соответствие итераций Definition of Done

| Итерация | DoD пункты | Статус |
|----------|------------|--------|
| Iteration 1 | DoD 1, 2 (vision + ADR) | ✅ Покрыто полностью |
| Iteration 2 | DoD 3 (Next.js init) | ✅ Покрыто полностью |
| Iteration 3 | DoD 4 (shadcn/ui) | ✅ Покрыто полностью |
| Iteration 4 | DoD 5, 6 (структура + типы) | ✅ Покрыто полностью |
| Iteration 5 | DoD 7 (ESLint/Prettier/TS) | ✅ Покрыто полностью |
| Iteration 6 | DoD 8, 9, 10, 11, 12 (Makefile + docs + roadmap) | ✅ Покрыто полностью |

### Зависимости между итерациями

| Итерация | Зависит от | Обоснование |
|----------|------------|-------------|
| Iteration 1 | - | Независимая (документация) |
| Iteration 2 | Iteration 1 | Требуется vision для архитектурных решений |
| Iteration 3 | Iteration 2 | Требуется Next.js проект для установки shadcn/ui |
| Iteration 4 | Iteration 3 | Требуются shadcn/ui компоненты для использования |
| Iteration 5 | Iteration 4 | Требуется структура проекта для настройки линтеров |
| Iteration 6 | Iteration 5 | Требуется завершенный проект для финализации |

✅ **Зависимости корректны - нет циклических зависимостей**

### Список создаваемых файлов по итерациям

**Iteration 1 (5 файлов):**
- `frontend/doc/frontend-vision.md`
- `frontend/doc/adr/001-nextjs-choice.md`
- `frontend/doc/adr/002-shadcn-ui-choice.md`
- `frontend/doc/adr/003-pnpm-choice.md`
- `frontend/doc/plans/s2-init-plan.md`

**Iteration 2 (3 файла):**
- `frontend/app/` (Next.js проект)
- `frontend/app/.env.local`
- `frontend/app/next.config.js` (обновление)

**Iteration 3 (8+ файлов):**
- `frontend/app/components.json`
- `frontend/app/src/components/ui/button.tsx`
- `frontend/app/src/components/ui/card.tsx`
- `frontend/app/src/components/ui/table.tsx`
- `frontend/app/src/components/ui/badge.tsx`
- `frontend/app/src/components/ui/select.tsx`
- `frontend/app/src/components/ui/dropdown-menu.tsx`
- `frontend/app/src/components/ui/chart.tsx`

**Iteration 4 (12+ файлов):**
- `frontend/app/src/app/layout.tsx`
- `frontend/app/src/app/page.tsx`
- `frontend/app/src/app/dashboard/page.tsx`
- `frontend/app/src/components/layout/header.tsx`
- `frontend/app/src/components/layout/sidebar.tsx`
- `frontend/app/src/components/layout/footer.tsx`
- `frontend/app/src/components/dashboard/stats-cards.tsx`
- `frontend/app/src/components/dashboard/activity-chart.tsx`
- `frontend/app/src/components/dashboard/recent-dialogs.tsx`
- `frontend/app/src/components/dashboard/top-users.tsx`
- `frontend/app/src/lib/api.ts`
- `frontend/app/src/lib/types.ts`
- `frontend/app/src/hooks/use-stats.ts`

**Iteration 5 (3 файла):**
- `frontend/app/.prettierrc`
- `frontend/app/.prettierignore`
- `frontend/app/.eslintrc.json` (обновление)
- `frontend/app/tsconfig.json` (обновление)

**Iteration 6 (4 файла):**
- `frontend/app/README.md`
- `frontend/app/.env.example`
- `Makefile` (обновление)
- `frontend/doc/frontend-roadmap.md` (обновление)
- `.gitignore` (обновление)

**Всего:** ~40+ файлов создано/обновлено

✅ **План консистентен - все файлы и задачи покрыты итерациями**

---

## Файлы для создания

### Документация (5 файлов)
1. `frontend/doc/frontend-vision.md` - техническое видение frontend
2. `frontend/doc/adr/001-nextjs-choice.md` - ADR по выбору Next.js
3. `frontend/doc/adr/002-shadcn-ui-choice.md` - ADR по выбору shadcn/ui
4. `frontend/doc/adr/003-pnpm-choice.md` - ADR по выбору pnpm
5. `frontend/app/README.md` - документация проекта

### Конфигурация (6 файлов)
6. `frontend/app/.prettierrc` - конфигурация Prettier
7. `frontend/app/.prettierignore` - игнорируемые файлы для Prettier
8. `frontend/app/.env.example` - пример переменных окружения
9. `frontend/app/next.config.js` - конфигурация Next.js (обновление)
10. `frontend/app/tsconfig.json` - конфигурация TypeScript (обновление)
11. `frontend/app/.eslintrc.json` - конфигурация ESLint (обновление)

### Код (10+ файлов)
12. `frontend/app/src/app/layout.tsx` - root layout
13. `frontend/app/src/app/page.tsx` - home page
14. `frontend/app/src/app/dashboard/page.tsx` - dashboard page
15. `frontend/app/src/components/layout/header.tsx` - header компонент
16. `frontend/app/src/components/layout/footer.tsx` - footer компонент
17. `frontend/app/src/lib/api.ts` - API client
18. `frontend/app/src/lib/types.ts` - TypeScript типы
19. `frontend/app/src/hooks/use-stats.ts` - custom hook для статистики
20. `frontend/app/src/components/dashboard/stats-cards.tsx` - заглушка
21. `frontend/app/src/components/dashboard/activity-chart.tsx` - заглушка
22. `frontend/app/src/components/dashboard/recent-dialogs.tsx` - заглушка
23. `frontend/app/src/components/dashboard/top-users.tsx` - заглушка

### Обновления (3 файла)
24. `Makefile` - добавить frontend команды
25. `frontend/doc/frontend-roadmap.md` - обновить статус FE-S2
26. `.gitignore` - добавить frontend игноры

---

## Зависимости

### Production
- next: ^15.0.0
- react: ^18.3.0
- react-dom: ^18.3.0
- typescript: ^5.6.0
- tailwindcss: ^3.4.0
- @radix-ui/react-*: (shadcn/ui зависимости)
- recharts: ^2.12.0 (для графиков)

### Development
- eslint: ^8.0.0
- eslint-config-next: ^15.0.0
- prettier: ^3.3.0
- @types/node: ^20.0.0
- @types/react: ^18.3.0

---

## Команды для выполнения

### Iteration 2: Инициализация проекта
```bash
cd frontend
pnpm create next-app@latest app --typescript --tailwind --app --src-dir --import-alias "@/*"
cd app
pnpm install
```

### Iteration 3: Установка shadcn/ui
```bash
cd frontend/app
pnpm dlx shadcn@latest init
pnpm dlx shadcn@latest add button card table badge select dropdown-menu chart
```

### Iteration 5: Установка дополнительных инструментов
```bash
cd frontend/app
pnpm add -D prettier eslint-plugin-jsx-a11y
```

---

## To-dos

- [ ] Iteration 1: Техническое видение и ADR документы
- [ ] Iteration 2: Инициализация Next.js проекта с TypeScript
- [ ] Iteration 3: Установка и настройка shadcn/ui компонентов
- [ ] Iteration 4: Создание структуры проекта и базовых компонентов
- [ ] Iteration 5: Настройка ESLint, Prettier и TypeScript strict mode
- [ ] Iteration 6: Makefile команды и документация
- [ ] Актуализация frontend-roadmap.md после выполнения спринта
- [ ] Добавление ссылки на план в таблицу спринтов в frontend-roadmap.md
- [ ] Проверка что все команды в package.json работают корректно (dev, build, lint, format, type-check)
- [ ] Тестирование подключения frontend к Mock API (GET /health, GET /api/v1/stats?period=day)

---

## Итоговый статус

**Статус:** 📋 Запланирован
**План создан:** 2025-10-17
**Готов к выполнению:** Да

---

*План создан: 2025-10-17*
*Последнее обновление: 2025-10-17*
*Статус: 📋 Запланирован*

