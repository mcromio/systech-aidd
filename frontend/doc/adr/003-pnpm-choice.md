# ADR-003: Выбор pnpm в качестве пакетного менеджера

**Дата**: 17 октября 2025
**Статус**: Принято
**Авторы**: Development Team

## Контекст

В спринте FE-S2 необходимо выбрать пакетный менеджер для frontend проекта. Требуется быстрый, эффективный инструмент, который хорошо работает с monorepo структурой (backend Python + frontend TypeScript) и современными JavaScript проектами.

## Рассматриваемые варианты

### 1. npm (Node Package Manager)

**Плюсы:**
- Установлен по умолчанию с Node.js
- Самый распространенный (все знают)
- Хорошая документация
- Работает везде без дополнительной установки

**Минусы:**
- Самый медленный из всех
- Большое использование дискового пространства (node_modules дублируются)
- Медленная установка зависимостей
- Phantom dependencies (можно импортировать пакеты не из dependencies)

### 2. Yarn Classic (v1)

**Плюсы:**
- Быстрее чем npm
- Offline cache
- Deterministic installs (lockfile)

**Минусы:**
- Deprecated (переходит на Yarn Berry)
- Все еще дублирует node_modules
- Медленнее чем pnpm

### 3. Yarn Berry (v2+)

**Плюсы:**
- Plug'n'Play (PnP) - без node_modules
- Очень быстрая установка
- Zero-installs возможность

**Минусы:**
- PnP ломает многие инструменты
- Сложная настройка
- Много breaking changes
- Не все пакеты совместимы с PnP
- Меньшее принятие в комьюнити

### 4. pnpm (Performance npm)

**Плюсы:**
- **Самый быстрый** пакетный менеджер
- **Минимальное дисковое пространство** (content-addressable storage)
- Strict dependency resolution (нет phantom dependencies)
- Отличная поддержка monorepo (workspaces)
- Совместим с npm (та же команды, та же экосистема)
- Активное развитие и комьюнити
- Работает со всеми инструментами (в отличие от Yarn PnP)

**Минусы:**
- Требует отдельной установки
- Меньшее распространение чем npm/yarn (но растет)
- Некоторые legacy пакеты могут иметь проблемы (редко)

## Решение

**Выбран pnpm**

## Обоснование

1. **Производительность**: pnpm значительно быстрее:
   - **3x быстрее** чем npm
   - **2x быстрее** чем Yarn Classic
   - Использует hard links вместо копирования файлов

2. **Эффективность дискового пространства**:
   - Один пакет хранится один раз на диске
   - Content-addressable storage
   - Экономия до 70% дискового пространства

3. **Strict mode по умолчанию**:
   - Нет phantom dependencies
   - Можно импортировать только явно указанные dependencies
   - Предотвращает баги от неявных зависимостей

4. **Monorepo support**: В будущем может понадобиться:
   ```
   systech-aidd_mcr/
   ├── backend/        # Python
   ├── frontend/app/   # TypeScript/React
   └── shared/         # Общие типы/утилиты
   ```
   pnpm workspaces идеально подходят для этого

5. **Совместимость**:
   - Работает со всеми инструментами (TypeScript, ESLint, Next.js и др.)
   - API совместим с npm (можно использовать `pnpm install` вместо `npm install`)

6. **Community**: Активно развивается, используется в крупных проектах:
   - Vue.js
   - Microsoft (некоторые проекты)
   - Prisma
   - shadcn/ui документация использует pnpm

7. **Developer Experience**:
   ```bash
   pnpm install  # Быстрая установка
   pnpm add react  # Добавить пакет
   pnpm dlx shadcn@latest add button  # Запустить binary без установки
   ```

8. **Lock file**: `pnpm-lock.yaml` более читаемый чем `package-lock.json`

## Сравнение производительности

| Операция | npm | Yarn | pnpm |
|----------|-----|------|------|
| Первая установка | 45s | 35s | **15s** |
| С cache | 25s | 15s | **5s** |
| Дисковое пространство | 200MB | 180MB | **70MB** |

*(Примерные значения для типичного Next.js проекта)*

## Последствия

### Положительные

- ✅ Самая быстрая установка зависимостей
- ✅ Минимальное использование дискового пространства
- ✅ Strict dependency resolution (меньше багов)
- ✅ Отличная поддержка monorepo
- ✅ Совместимость со всеми инструментами
- ✅ Активное комьюнити и развитие

### Отрицательные

- ⚠️ Требует отдельной установки (один раз)
- ⚠️ Команда может быть незнакома (но API как у npm)
- ⚠️ Редкие проблемы с legacy пакетами

### Риски и митигации

- **Риск**: Команда не знакома с pnpm
  **Митигация**: API практически идентичен npm, все работает также

- **Риск**: CI/CD pipelines нужно настроить
  **Митигация**: Добавить установку pnpm в pipeline (одна строка)

- **Риск**: Legacy пакеты могут иметь проблемы
  **Митигация**: `.npmrc` с настройками совместимости, если нужно

## Установка

```bash
# Windows (PowerShell)
iwr https://get.pnpm.io/install.ps1 -useb | iex

# macOS/Linux
curl -fsSL https://get.pnpm.io/install.sh | sh -

# или через npm (если уже есть)
npm install -g pnpm

# Проверка
pnpm --version
```

## Конфигурация

```.npmrc
# .npmrc (если нужно)
# strict-peer-dependencies=false  # Если нужна совместимость
# shamefully-hoist=false           # По умолчанию strict mode
```

## Основные команды

```bash
# Установка зависимостей
pnpm install  # или просто pnpm i

# Добавить зависимость
pnpm add react
pnpm add -D typescript  # dev dependency

# Удалить зависимость
pnpm remove react

# Запуск скриптов
pnpm dev
pnpm build
pnpm test

# Запуск binary без установки
pnpm dlx create-next-app
pnpm dlx shadcn@latest add button

# Обновление зависимостей
pnpm update
pnpm update -L  # latest versions

# Очистка cache
pnpm store prune
```

## Интеграция с проектом

```json
// package.json
{
  "name": "frontend-app",
  "packageManager": "pnpm@9.0.0",  // Указываем версию pnpm
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

```makefile
# Makefile
fe-install:  ## Установить frontend зависимости
	cd frontend/app && pnpm install

fe-dev:  ## Запустить frontend dev сервер
	cd frontend/app && pnpm dev
```

## Альтернативы в будущем

Если потребуется:
- **Yarn Berry**: Если нужен Zero-installs (редко)
- **Bun**: Новый ultra-fast runtime + package manager (когда станет stable)

## Ссылки

- [pnpm Documentation](https://pnpm.io/)
- [pnpm Benchmarks](https://pnpm.io/benchmarks)
- [pnpm vs npm vs Yarn](https://pnpm.io/feature-comparison)
- [pnpm Workspaces](https://pnpm.io/workspaces)

