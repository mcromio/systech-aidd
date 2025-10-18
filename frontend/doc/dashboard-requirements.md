# Функциональные требования к Dashboard статистики

> **Версия:** 1.0
> **Дата:** 2025-10-17
> **Спринт:** FE-S1
> **Референс:** https://ui.shadcn.com/blocks#dashboard-01

---

## 1. Обзор

Dashboard предназначен для визуализации статистики диалогов пользователей с LLM-ассистентом. Интерфейс должен предоставлять администратору полную картину активности системы за выбранный период времени.

---

## 2. Метрики для отображения

### 2.1 Общая статистика (Cards)

Четыре ключевые метрики в виде карточек в верхней части dashboard:

#### Метрика 1: Всего диалогов
- **Название:** "Всего диалогов" / "Total Dialogs"
- **Значение:** Общее количество уникальных диалогов (по user_id)
- **Дополнительно:** Процент изменения относительно предыдущего периода
- **Пример:** `245 диалогов (+12.5% от предыдущего периода)`

#### Метрика 2: Активные пользователи
- **Название:** "Активные пользователи" / "Active Users"
- **Значение:** Количество уникальных пользователей, отправивших хотя бы одно сообщение
- **Дополнительно:** Процент изменения относительно предыдущего периода
- **Пример:** `89 пользователей (+8.2% от предыдущего периода)`

#### Метрика 3: Всего сообщений
- **Название:** "Всего сообщений" / "Total Messages"
- **Значение:** Общее количество сообщений (пользовательские + ассистент)
- **Дополнительно:** Процент изменения относительно предыдущего периода
- **Пример:** `1,543 сообщений (+15.3% от предыдущего периода)`

#### Метрика 4: Средняя длина диалога
- **Название:** "Средняя длина диалога" / "Avg Dialog Length"
- **Значение:** Среднее количество сообщений на один диалог
- **Дополнительно:** Процент изменения относительно предыдущего периода
- **Пример:** `6.3 сообщений (-2.1% от предыдущего периода)`

---

### 2.2 График активности (Chart)

Визуализация активности пользователей по времени:

#### Характеристики графика
- **Тип:** Line chart (линейный график) или Bar chart (столбчатый)
- **Ось X:** Временные интервалы (зависит от выбранного периода)
  - **Day:** 24 точки (почасовая активность: 00:00, 01:00, ..., 23:00)
  - **Week:** 7 точек (ежедневная активность: Пн, Вт, Ср, Чт, Пт, Сб, Вс)
  - **Month:** 30-31 точка (ежедневная активность: 1, 2, 3, ..., 30/31)
- **Ось Y:** Количество сообщений
- **Данные:** Количество сообщений в каждом временном интервале
- **Интерактивность:** Tooltip при наведении (показывает точное значение)

#### Пример данных
```json
[
  {"time": "00:00", "messages": 12},
  {"time": "01:00", "messages": 8},
  {"time": "02:00", "messages": 5},
  ...
  {"time": "23:00", "messages": 15}
]
```

---

### 2.3 Последние диалоги (Recent Dialogs Table)

Таблица с информацией о последних 10 диалогах:

#### Колонки таблицы

1. **User** (Пользователь)
   - Формат: `@username` или `FirstName LastName` (если username отсутствует)
   - Пример: `@john_doe`, `Иван Петров`

2. **Messages** (Сообщений)
   - Количество сообщений в диалоге
   - Пример: `8`, `15`, `3`

3. **Last Active** (Последняя активность)
   - Относительное время последнего сообщения
   - Формат: "N минут назад", "N часов назад", "N дней назад"
   - Пример: `5 минут назад`, `2 часа назад`, `1 день назад`

4. **Status** (Статус)
   - Badge с статусом диалога:
     - **Active** (зеленый) - есть активность в последние 5 минут
     - **Idle** (желтый) - активность была в последний час
     - **Inactive** (серый) - активность была давно
   - Пример: `Active`, `Idle`, `Inactive`

#### Сортировка
- По умолчанию: по последней активности (newest first)
- Ограничение: 10 записей

---

### 2.4 Топ пользователей (Top Users)

Список самых активных пользователей за период:

#### Характеристики

1. **User** (Пользователь)
   - Аватар (первая буква имени) + имя пользователя
   - Формат: `@username` или `FirstName LastName`
   - Пример: `@john_doe`, `Мария Сидорова`

2. **Messages** (Сообщений)
   - Общее количество отправленных сообщений
   - Пример: `156`, `98`, `67`

3. **Progress Bar** (Прогресс бар)
   - Визуальное представление активности относительно самого активного
   - 100% = самый активный пользователь
   - Пример: Top-1 = 100%, Top-2 = 75%, Top-3 = 50%

#### Сортировка
- По количеству сообщений (descending)
- Ограничение: Топ-5 пользователей

---

## 3. Фильтр периода

### Выбор периода (Period Selector)

Dropdown или tabs для выбора периода анализа:

- **Day** (За день) - статистика за последние 24 часа
- **Week** (За неделю) - статистика за последние 7 дней
- **Month** (За месяц) - статистика за последние 30 дней

**Поведение:**
- При изменении периода все метрики и графики обновляются
- Отправляется запрос к API: `GET /api/v1/stats?period=day|week|month`

---

## 4. Структура данных (на основе БД)

### Существующие таблицы

#### Таблица `users`
```sql
- id (int, PK)
- telegram_id (bigint, unique)
- username (varchar, nullable)
- first_name (varchar, nullable)
- last_name (varchar, nullable)
- created_at (timestamp)
- last_seen_at (timestamp, nullable)
```

#### Таблица `messages`
```sql
- id (int, PK)
- user_id (int, FK -> users.id)
- role (varchar: 'user' | 'assistant' | 'system')
- content (text)
- tool_calls (jsonb, nullable)
- created_at (timestamp)
```

### Расчет метрик

#### Всего диалогов
```sql
SELECT COUNT(DISTINCT user_id)
FROM messages
WHERE created_at >= NOW() - INTERVAL '1 DAY' -- для period=day
```

#### Активные пользователи
```sql
SELECT COUNT(DISTINCT user_id)
FROM messages
WHERE role = 'user'
  AND created_at >= NOW() - INTERVAL '1 DAY'
```

#### Всего сообщений
```sql
SELECT COUNT(*)
FROM messages
WHERE created_at >= NOW() - INTERVAL '1 DAY'
```

#### Средняя длина диалога
```sql
SELECT AVG(message_count)
FROM (
  SELECT user_id, COUNT(*) as message_count
  FROM messages
  WHERE created_at >= NOW() - INTERVAL '1 DAY'
  GROUP BY user_id
) subquery
```

#### График активности (почасовая для day)
```sql
SELECT
  DATE_TRUNC('hour', created_at) as hour,
  COUNT(*) as messages
FROM messages
WHERE created_at >= NOW() - INTERVAL '1 DAY'
GROUP BY hour
ORDER BY hour
```

#### Последние диалоги
```sql
SELECT
  u.username,
  u.first_name,
  u.last_name,
  COUNT(m.id) as message_count,
  MAX(m.created_at) as last_active
FROM users u
JOIN messages m ON u.id = m.user_id
WHERE m.created_at >= NOW() - INTERVAL '1 DAY'
GROUP BY u.id, u.username, u.first_name, u.last_name
ORDER BY last_active DESC
LIMIT 10
```

#### Топ пользователей
```sql
SELECT
  u.username,
  u.first_name,
  u.last_name,
  COUNT(m.id) as message_count
FROM users u
JOIN messages m ON u.id = m.user_id
WHERE m.created_at >= NOW() - INTERVAL '1 DAY'
  AND m.role = 'user'
GROUP BY u.id, u.username, u.first_name, u.last_name
ORDER BY message_count DESC
LIMIT 5
```

---

## 5. UX требования

### Адаптивный дизайн
- Desktop: 4 колонки для cards, 2 колонки для chart + recent dialogs
- Tablet: 2 колонки для cards, 1 колонка для остального
- Mobile: 1 колонка, стекирование элементов

### Загрузка данных
- Показать skeleton loaders во время загрузки
- Обработка ошибок: показать toast notification
- Refresh button для обновления данных

### Интерактивность
- Hover effects на таблицах и карточках
- Tooltip на графике для точных значений
- Smooth transitions при смене периода

---

## 6. Цветовая схема (из референса shadcn/ui)

- **Primary:** Синий (#0ea5e9)
- **Success:** Зеленый (#22c55e)
- **Warning:** Желтый (#eab308)
- **Danger:** Красный (#ef4444)
- **Neutral:** Серый (#64748b)
- **Background:** Белый (#ffffff) / Dark: (#0f172a)

---

## 7. Примеры значений (для Mock API)

### General Stats
```json
{
  "total_dialogs": 245,
  "total_dialogs_change": 12.5,
  "active_users": 89,
  "active_users_change": 8.2,
  "total_messages": 1543,
  "total_messages_change": 15.3,
  "avg_dialog_length": 6.3,
  "avg_dialog_length_change": -2.1
}
```

### Activity Chart (Day)
```json
[
  {"time": "00:00", "messages": 12},
  {"time": "01:00", "messages": 8},
  {"time": "02:00", "messages": 5},
  ...
  {"time": "23:00", "messages": 15}
]
```

### Recent Dialogs
```json
[
  {
    "user": "@john_doe",
    "messages": 8,
    "last_active": "5 минут назад",
    "status": "active"
  },
  {
    "user": "Иван Петров",
    "messages": 15,
    "last_active": "2 часа назад",
    "status": "idle"
  }
]
```

### Top Users
```json
[
  {
    "user": "@maria_s",
    "messages": 156,
    "percentage": 100
  },
  {
    "user": "Петр Иванов",
    "messages": 98,
    "percentage": 62.8
  }
]
```

---

## 8. API Requirements Summary

### Endpoint
```
GET /api/v1/stats?period=day|week|month
```

### Response Structure
```json
{
  "period": "day",
  "general_stats": { ... },
  "activity_chart": [ ... ],
  "recent_dialogs": [ ... ],
  "top_users": [ ... ]
}
```

### Требования к данным Mock API
- Данные должны быть реалистичными
- Разные значения для разных периодов (day/week/month)
- Консистентность данных (сумма активности = total_messages)
- Даты и времена в актуальном диапазоне
- Имена пользователей разнообразные (русские и латинские)

---

**Статус:** ✅ Требования определены
**Следующий шаг:** Проектирование API контракта (Iteration 2)

