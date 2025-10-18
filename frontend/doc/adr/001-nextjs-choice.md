# ADR-001: Выбор Next.js в качестве React фреймворка

**Дата**: 17 октября 2025
**Статус**: Принято
**Авторы**: Development Team

## Контекст

В спринте FE-S2 необходимо выбрать React фреймворк для разработки веб-интерфейса dashboard статистики диалогов LLM-ассистента. Требуется современный, производительный и поддерживаемый фреймворк с хорошей экосистемой.

## Рассматриваемые варианты

### 1. Create React App (CRA)

**Плюсы:**
- Простая настройка из коробки
- Минимальная конфигурация
- Хорошо известен разработчикам

**Минусы:**
- Deprecated (больше не поддерживается React командой)
- Нет SSR/SSG из коробки
- Медленная сборка (webpack)
- Большой bundle size
- Нет file-based routing
- Требует ejecting для кастомизации

### 2. Vite + React

**Плюсы:**
- Очень быстрая сборка (esbuild)
- Мгновенный hot-reload
- Легковесный dev server
- Минимальная конфигурация
- Хорошая экосистема плагинов

**Минусы:**
- Нет SSR/SSG из коробки (нужен Vite SSR или Vite-plugin-ssr)
- Нужно настраивать routing вручную (React Router)
- Меньше "convention over configuration"
- Больше manual setup для production-ready приложения

### 3. Next.js

**Плюсы:**
- Production-ready из коробки
- SSR, SSG, ISR поддержка
- File-based routing (App Router)
- Server Components и Client Components
- Встроенная оптимизация (Image, Font, Script)
- API routes (если потребуется)
- Отличная производительность (Turbopack)
- Большое комьюнити и экосистема
- Официально рекомендован React командой
- Vercel поддержка для простого deployment

**Минусы:**
- Больше концепций для изучения (SSR, RSC)
- Более сложная архитектура
- Vendor lock-in с Vercel (опционально)
- Heavier чем простой SPA

### 4. Remix

**Плюсы:**
- Фокус на Web Standards (Fetch API, FormData)
- Отличный DX для работы с формами
- Nested routing
- Progressive enhancement

**Минусы:**
- Меньшее комьюнити по сравнению с Next.js
- Меньше готовых решений и примеров
- Более сложная кривая обучения

## Решение

**Выбран Next.js 15 (App Router)**

## Обоснование

1. **Production-ready**: Next.js предоставляет все необходимое для production из коробки - SSR, оптимизация, image optimization, автоматический code splitting

2. **App Router**: Новый App Router (stable в Next.js 13+) предоставляет:
   - File-based routing
   - Layouts и nested layouts
   - Server Components по умолчанию
   - Streaming и Suspense
   - Лучшую производительность

3. **Performance**:
   - Automatic code splitting
   - Image optimization из коробки
   - Font optimization
   - Script optimization
   - Incremental Static Regeneration (ISR)

4. **Developer Experience**:
   - Hot-reload с Fast Refresh
   - TypeScript support из коробки
   - Built-in ESLint configuration
   - Отличная документация
   - Large community

5. **Экосистема**:
   - Работает с shadcn/ui без доп. настройки
   - Tailwind CSS интеграция из коробки
   - Vercel deployment за пару кликов (если потребуется)

6. **Future-proof**: Официально рекомендован React командой, активное развитие, большое комьюнити

7. **Простота для нашего случая**:
   - Dashboard не требует сложного SSR
   - Можно использовать как SPA с Client Components
   - При необходимости легко добавить SSR/SSG

## Последствия

### Положительные

- ✅ Готовность к production без дополнительной настройки
- ✅ Отличная производительность из коробки
- ✅ File-based routing упрощает навигацию
- ✅ Большое комьюнити и множество примеров
- ✅ Легкая интеграция с shadcn/ui и Tailwind CSS
- ✅ Простой deployment (Vercel, Docker и др.)

### Отрицательные

- ⚠️ Больше концепций для изучения (Server vs Client Components)
- ⚠️ Heavier чем простой Vite + React
- ⚠️ Некоторые features могут быть избыточны для нашего dashboard

### Риски и митигации

- **Риск**: Сложность Server Components для команды
  **Митигация**: Используем преимущественно Client Components (use client), Server Components опционально

- **Риск**: Overhead для простого SPA
  **Митигация**: Next.js можно использовать как обычный React с Client Components, сложные features опциональны

- **Риск**: Vendor lock-in с Vercel
  **Митигация**: Next.js можно деплоить куда угодно (Docker, самостоятельный хостинг), Vercel опционален

## Конфигурация

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // API proxy для Mock API
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
```

## Альтернативы в будущем

Если потребуется:
- **Меньший bundle**: Preact вместо React
- **Статический сайт**: Next.js Static Export (`next export`)
- **Простой SPA**: Можно использовать Next.js с output: 'export'

## Ссылки

- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js App Router](https://nextjs.org/docs/app)
- [React Recommendations](https://react.dev/learn/start-a-new-react-project)
- [Next.js Examples](https://github.com/vercel/next.js/tree/canary/examples)

