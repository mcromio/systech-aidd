# ADR-002: Выбор shadcn/ui в качестве UI библиотеки

**Дата**: 17 октября 2025
**Статус**: Принято
**Авторы**: Development Team

## Контекст

В спринте FE-S2 необходимо выбрать UI библиотеку для быстрой разработки dashboard интерфейса. Требуется современная, доступная (accessible), кастомизируемая библиотека компонентов, совместимая с Tailwind CSS и Next.js.

## Рассматриваемые варианты

### 1. Material UI (MUI)

**Плюсы:**
- Самая популярная React UI библиотека
- Огромное количество компонентов
- Большое комьюнити
- Production-ready
- Хорошая документация

**Минусы:**
- Очень тяжелая (большой bundle size)
- Сложно кастомизировать дизайн
- Material Design может не подходить под наш стиль
- Конфликты с Tailwind CSS
- Styled-components/Emotion зависимости

### 2. Ant Design

**Плюсы:**
- Полный набор компонентов для dashboard
- Production-tested в enterprise проектах
- Хорошая документация на китайском и английском

**Минусы:**
- Большой bundle size
- Специфичный китайский стиль дизайна
- Сложная кастомизация
- Less/CSS modules вместо Tailwind

### 3. Chakra UI

**Плюсы:**
- Отличная accessibility
- Хорошая интеграция с React
- Модульная архитектура
- Темизация из коробки

**Минусы:**
- Свой CSS-in-JS подход (не Tailwind)
- Средний bundle size
- Меньшее комьюнити чем MUI

### 4. Headless UI + собственные стили

**Плюсы:**
- Минимальный bundle size
- Полный контроль над дизайном
- Отличная accessibility (от Tailwind Labs)
- Идеально для Tailwind CSS

**Минусы:**
- Мало готовых компонентов
- Много работы по созданию UI с нуля
- Нужно самим реализовывать сложные компоненты

### 5. shadcn/ui

**Плюсы:**
- **Не библиотека, а коллекция копируемых компонентов**
- Код компонентов в вашем репозитории (полный контроль)
- Построен на Radix UI (отличная accessibility)
- Идеально работает с Tailwind CSS
- Современный дизайн из коробки
- Легко кастомизировать
- Минимальный bundle (только то что используете)
- TypeScript из коробки
- Активное комьюнити
- Множество готовых blocks и примеров

**Минусы:**
- Относительно новый проект
- Меньше компонентов чем в MUI/Ant Design
- Нужно копировать код компонентов (но это и плюс)

## Решение

**Выбран shadcn/ui**

## Обоснование

1. **Copy & Paste подход**: shadcn/ui не устанавливается как npm пакет. Компоненты копируются в ваш проект через CLI. Это дает:
   - Полный контроль над кодом компонентов
   - Возможность кастомизации без hacks
   - Нет vendor lock-in
   - Минимальный bundle size

2. **Radix UI Foundation**: Построен на Radix UI Primitives:
   - Отличная accessibility (ARIA, keyboard navigation)
   - Unstyled primitives
   - Production-ready
   - Хорошо протестированы

3. **Tailwind CSS Integration**: Идеально работает с Tailwind:
   - Все стили через Tailwind classes
   - Легко кастомизировать
   - CSS Variables для тем
   - Responsive design через Tailwind breakpoints

4. **TypeScript First**: Все компоненты типизированы из коробки

5. **Blocks и Examples**:
   - Готовые dashboard blocks
   - Наш референс (shadcn/ui blocks#dashboard-01) уже реализован
   - Много примеров для копирования

6. **Community**: Активное и растущее комьюнити, множество примеров

7. **Next.js Integration**: Отлично работает с Next.js App Router из коробки

8. **Developer Experience**:
   ```bash
   pnpm dlx shadcn@latest add button
   ```
   Компонент копируется в `src/components/ui/` - можно сразу кастомизировать

9. **Minimal Bundle**: Только компоненты которые вы используете попадают в bundle

10. **Modern Design**: Современный, чистый дизайн который легко адаптировать

## Последствия

### Положительные

- ✅ Полный контроль над кодом компонентов
- ✅ Минимальный bundle size
- ✅ Легкая кастомизация под наш дизайн
- ✅ Отличная accessibility из коробки (Radix UI)
- ✅ TypeScript support
- ✅ Идеальная интеграция с Tailwind CSS
- ✅ Нет vendor lock-in
- ✅ Готовые dashboard blocks из референса

### Отрицательные

- ⚠️ Компоненты нужно копировать в проект (но это быстро через CLI)
- ⚠️ Меньше компонентов чем в MUI (но достаточно для dashboard)
- ⚠️ Относительно новый (но стабильный и активный)

### Риски и митигации

- **Риск**: Недостаточно компонентов для будущих features
  **Митигация**: shadcn/ui активно развивается, добавляются новые компоненты. Можно создать свои на базе Radix UI

- **Риск**: Код компонентов в репозитории (нужно обновлять вручную)
  **Митигация**: CLI позволяет легко обновить компоненты. Обновления нечастые, и можно контролировать

- **Риск**: Команда не знакома с Radix UI
  **Митигация**: Компоненты уже готовы, достаточно использовать их API. Radix UI документация отличная

## Установка и конфигурация

```bash
# 1. Инициализация
pnpm dlx shadcn@latest init

# 2. Установка компонентов
pnpm dlx shadcn@latest add button card table badge

# 3. Компоненты появляются в src/components/ui/
```

## Конфигурация

```json
// components.json
{
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/app/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

## Использование

```typescript
// Просто импортируем и используем
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function StatsCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Total Dialogs</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-bold">245</p>
        <Button>View Details</Button>
      </CardContent>
    </Card>
  );
}
```

## Альтернативы в будущем

Если потребуется:
- **Больше компонентов**: Можно добавить Radix UI primitives напрямую
- **Другой дизайн**: Легко изменить через Tailwind classes
- **Темизация**: CSS Variables + Tailwind позволяют легко создавать темы

## Ссылки

- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [shadcn/ui Blocks](https://ui.shadcn.com/blocks)
- [Radix UI Primitives](https://www.radix-ui.com/)
- [Dashboard Reference](https://ui.shadcn.com/blocks#dashboard-01)

