# API Contract: Stats API

> **Версия:** 1.0
> **Дата:** 2025-10-17
> **Спринт:** FE-S1
> **Base URL:** `http://localhost:8000`

---

## Обзор

REST API для получения статистики диалогов LLM-ассистента. Предоставляет агрегированные данные за выбранный период времени (день, неделя, месяц).

**Принципы:**
- KISS подход: один endpoint для всей статистики
- JSON формат ответа
- Query параметры для фильтрации
- OpenAPI/Swagger документация
- CORS enabled для frontend разработки

---

## Endpoints

### 1. Health Check

Проверка работоспособности API сервера.

```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "ok"
}
```

---

### 2. Get Stats

Получение статистики диалогов за период.

```http
GET /api/v1/stats?period={day|week|month}
```

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `period` | string | No | `day` | Период анализа: `day`, `week`, `month` |

#### Response: `200 OK`

```json
{
  "period": "day",
  "generated_at": "2025-10-17T11:05:00Z",
  "general_stats": {
    "total_dialogs": 245,
    "total_dialogs_change": 12.5,
    "active_users": 89,
    "active_users_change": 8.2,
    "total_messages": 1543,
    "total_messages_change": 15.3,
    "avg_dialog_length": 6.3,
    "avg_dialog_length_change": -2.1
  },
  "activity_chart": [
    {
      "time": "00:00",
      "messages": 12
    },
    {
      "time": "01:00",
      "messages": 8
    }
  ],
  "recent_dialogs": [
    {
      "user_display": "@john_doe",
      "message_count": 8,
      "last_active": "5 минут назад",
      "status": "active"
    }
  ],
  "top_users": [
    {
      "user_display": "@maria_s",
      "message_count": 156,
      "percentage": 100.0
    }
  ]
}
```

#### Error Responses

**400 Bad Request** - Невалидный параметр period
```json
{
  "detail": "Invalid period value. Must be one of: day, week, month"
}
```

**500 Internal Server Error** - Внутренняя ошибка сервера
```json
{
  "detail": "Internal server error"
}
```

---

## Data Models

### StatsResponse

Корневая модель ответа API.

```python
class StatsResponse(BaseModel):
    period: Literal["day", "week", "month"]
    generated_at: datetime
    general_stats: GeneralStats
    activity_chart: list[ActivityDataPoint]
    recent_dialogs: list[DialogInfo]
    top_users: list[UserActivity]
```

---

### GeneralStats

Общая статистика за период.

```python
class GeneralStats(BaseModel):
    total_dialogs: int
    total_dialogs_change: float
    active_users: int
    active_users_change: float
    total_messages: int
    total_messages_change: float
    avg_dialog_length: float
    avg_dialog_length_change: float
```

**Описание полей:**

- `total_dialogs` - Общее количество уникальных диалогов (по user_id)
- `total_dialogs_change` - Процент изменения относительно предыдущего периода (±%)
- `active_users` - Количество активных пользователей
- `active_users_change` - Процент изменения активных пользователей (±%)
- `total_messages` - Общее количество сообщений (user + assistant)
- `total_messages_change` - Процент изменения сообщений (±%)
- `avg_dialog_length` - Среднее количество сообщений на диалог
- `avg_dialog_length_change` - Процент изменения средней длины (±%)

**Пример:**
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

---

### ActivityDataPoint

Точка данных для графика активности.

```python
class ActivityDataPoint(BaseModel):
    time: str
    messages: int
```

**Описание полей:**

- `time` - Временная метка (формат зависит от периода)
  - **day:** "00:00", "01:00", ..., "23:00" (24 точки)
  - **week:** "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс" (7 точек)
  - **month:** "1", "2", "3", ..., "30" (30 точек)
- `messages` - Количество сообщений в этом интервале

**Пример для period=day:**
```json
[
  {"time": "00:00", "messages": 12},
  {"time": "01:00", "messages": 8},
  {"time": "02:00", "messages": 5},
  {"time": "03:00", "messages": 3}
]
```

**Пример для period=week:**
```json
[
  {"time": "Пн", "messages": 234},
  {"time": "Вт", "messages": 189},
  {"time": "Ср", "messages": 256}
]
```

---

### DialogInfo

Информация о диалоге пользователя.

```python
class DialogInfo(BaseModel):
    user_display: str
    message_count: int
    last_active: str
    status: Literal["active", "idle", "inactive"]
```

**Описание полей:**

- `user_display` - Отображаемое имя пользователя
  - Формат: `@username` или `FirstName LastName` (если username отсутствует)
- `message_count` - Количество сообщений в диалоге
- `last_active` - Относительное время последней активности
  - Формат: "N минут назад", "N часов назад", "N дней назад"
- `status` - Статус диалога:
  - `active` - активность в последние 5 минут
  - `idle` - активность в последний час
  - `inactive` - активность давно

**Пример:**
```json
[
  {
    "user_display": "@john_doe",
    "message_count": 8,
    "last_active": "5 минут назад",
    "status": "active"
  },
  {
    "user_display": "Иван Петров",
    "message_count": 15,
    "last_active": "2 часа назад",
    "status": "idle"
  },
  {
    "user_display": "@maria_s",
    "message_count": 23,
    "last_active": "1 день назад",
    "status": "inactive"
  }
]
```

---

### UserActivity

Активность пользователя (для топа).

```python
class UserActivity(BaseModel):
    user_display: str
    message_count: int
    percentage: float
```

**Описание полей:**

- `user_display` - Отображаемое имя пользователя
  - Формат: `@username` или `FirstName LastName`
- `message_count` - Общее количество отправленных сообщений
- `percentage` - Процент активности относительно самого активного (0-100)
  - 100.0 = самый активный пользователь
  - Остальные пропорционально

**Пример:**
```json
[
  {
    "user_display": "@maria_s",
    "message_count": 156,
    "percentage": 100.0
  },
  {
    "user_display": "Петр Иванов",
    "message_count": 98,
    "percentage": 62.8
  },
  {
    "user_display": "@alex_k",
    "message_count": 78,
    "percentage": 50.0
  }
]
```

---

## Примеры использования

### Пример 1: Получить статистику за день

**Request:**
```bash
curl "http://localhost:8000/api/v1/stats?period=day"
```

**Response:** `200 OK`
```json
{
  "period": "day",
  "generated_at": "2025-10-17T11:05:00Z",
  "general_stats": {
    "total_dialogs": 245,
    "total_dialogs_change": 12.5,
    "active_users": 89,
    "active_users_change": 8.2,
    "total_messages": 1543,
    "total_messages_change": 15.3,
    "avg_dialog_length": 6.3,
    "avg_dialog_length_change": -2.1
  },
  "activity_chart": [
    {"time": "00:00", "messages": 12},
    {"time": "01:00", "messages": 8}
  ],
  "recent_dialogs": [
    {
      "user_display": "@john_doe",
      "message_count": 8,
      "last_active": "5 минут назад",
      "status": "active"
    }
  ],
  "top_users": [
    {
      "user_display": "@maria_s",
      "message_count": 156,
      "percentage": 100.0
    }
  ]
}
```

---

### Пример 2: Получить статистику за неделю

**Request:**
```bash
curl "http://localhost:8000/api/v1/stats?period=week"
```

**Response:** `200 OK`
```json
{
  "period": "week",
  "generated_at": "2025-10-17T11:05:00Z",
  "general_stats": {
    "total_dialogs": 856,
    "total_dialogs_change": 18.7,
    "active_users": 234,
    "active_users_change": 12.3,
    "total_messages": 5432,
    "total_messages_change": 22.1,
    "avg_dialog_length": 6.3,
    "avg_dialog_length_change": 3.2
  },
  "activity_chart": [
    {"time": "Пн", "messages": 789},
    {"time": "Вт", "messages": 823},
    {"time": "Ср", "messages": 756}
  ],
  "recent_dialogs": [...],
  "top_users": [...]
}
```

---

### Пример 3: Невалидный период

**Request:**
```bash
curl "http://localhost:8000/api/v1/stats?period=invalid"
```

**Response:** `400 Bad Request`
```json
{
  "detail": "Invalid period value. Must be one of: day, week, month"
}
```

---

## StatCollector Protocol

Интерфейс для реализации сборщика статистики (Mock и Real).

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class StatCollector(Protocol):
    """
    Протокол для сборщиков статистики.

    Реализации:
    - MockStatCollector: генерация тестовых данных
    - RealStatCollector: сбор реальных данных из БД (FE-S5)
    """

    def get_stats(self, period: Literal["day", "week", "month"]) -> StatsResponse:
        """
        Получить статистику за период.

        Args:
            period: Период анализа (day, week, month)

        Returns:
            StatsResponse с агрегированными данными

        Raises:
            ValueError: Если period невалиден
        """
        ...
```

---

## Технические детали

### CORS Configuration

Для разработки фронтенда API должен разрешать CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite/React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### OpenAPI Documentation

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

### Валидация параметров

FastAPI автоматически валидирует query параметры через Pydantic. Для `period` используем Enum или Literal для ограничения допустимых значений.

---

## Changelog

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0 | 2025-10-17 | Первая версия API контракта |

---

**Статус:** ✅ API контракт спроектирован
**Следующий шаг:** Реализация Pydantic моделей (src/api/models.py)

