# API Usage Guide: Mock Stats API

> **Версия:** 1.0
> **Дата:** 2025-10-17
> **Спринт:** FE-S1

---

## Обзор

Это руководство описывает как использовать Mock Stats API для разработки frontend приложения. API предоставляет тестовые данные для dashboard статистики диалогов.

**Base URL:** `http://localhost:8000`

---

## Быстрый старт

### 1. Запуск API сервера

```bash
# Через Makefile (рекомендуется)
make api-run

# Или напрямую через Python
python -m src.api_main

# Или через uvicorn с hot-reload
uvicorn src.api_main:app --reload --port 8000
```

API будет доступен на `http://localhost:8000`

### 2. Проверка работоспособности

```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "ok"
}
```

### 3. Получение статистики

```bash
curl "http://localhost:8000/api/v1/stats?period=day"
```

---

## Endpoints

### 1. Health Check

Проверка работоспособности API.

```http
GET /health
```

**Пример запроса:**
```bash
curl http://localhost:8000/health
```

**Ответ:** `200 OK`
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

**Query Parameters:**
- `period` (optional, default: `day`): Период анализа
  - `day` - последние 24 часа
  - `week` - последние 7 дней
  - `month` - последние 30 дней

---

## Примеры использования

### JavaScript / Fetch API

```javascript
// Получение статистики за день
async function getStats(period = 'day') {
  const response = await fetch(`http://localhost:8000/api/v1/stats?period=${period}`);
  const data = await response.json();
  return data;
}

// Использование
const stats = await getStats('day');
console.log('Total dialogs:', stats.general_stats.total_dialogs);
console.log('Active users:', stats.general_stats.active_users);
```

---

### React Hook

```javascript
import { useState, useEffect } from 'react';

function useStats(period = 'day') {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/api/v1/stats?period=${period}`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, [period]);

  return { stats, loading, error };
}

// Использование в компоненте
function Dashboard() {
  const { stats, loading, error } = useStats('day');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Dialogs: {stats.general_stats.total_dialogs}</h1>
      <h2>Active Users: {stats.general_stats.active_users}</h2>
    </div>
  );
}
```

---

### Axios

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Настройка Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Получение статистики
export async function fetchStats(period = 'day') {
  try {
    const response = await api.get('/api/v1/stats', {
      params: { period }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    throw error;
  }
}

// Использование
const stats = await fetchStats('week');
```

---

### Vue.js Composable

```javascript
import { ref, watchEffect } from 'vue';

export function useStats(period = ref('day')) {
  const stats = ref(null);
  const loading = ref(false);
  const error = ref(null);

  watchEffect(async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/stats?period=${period.value}`);
      if (!response.ok) throw new Error('Failed to fetch');
      stats.value = await response.json();
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  });

  return { stats, loading, error };
}
```

---

### cURL примеры

#### Статистика за день
```bash
curl -X GET "http://localhost:8000/api/v1/stats?period=day" \
  -H "Accept: application/json"
```

#### Статистика за неделю
```bash
curl -X GET "http://localhost:8000/api/v1/stats?period=week" \
  -H "Accept: application/json"
```

#### Статистика за месяц
```bash
curl -X GET "http://localhost:8000/api/v1/stats?period=month" \
  -H "Accept: application/json"
```

#### С форматированием JSON (jq)
```bash
curl -s "http://localhost:8000/api/v1/stats?period=day" | jq .
```

#### Извлечение конкретных данных (jq)
```bash
# Только общая статистика
curl -s "http://localhost:8000/api/v1/stats?period=day" | jq '.general_stats'

# Только количество диалогов
curl -s "http://localhost:8000/api/v1/stats?period=day" | jq '.general_stats.total_dialogs'

# График активности
curl -s "http://localhost:8000/api/v1/stats?period=day" | jq '.activity_chart'

# Топ пользователи
curl -s "http://localhost:8000/api/v1/stats?period=day" | jq '.top_users'
```

---

### Python / requests

```python
import requests

API_BASE_URL = "http://localhost:8000"

def get_stats(period: str = "day") -> dict:
    """Получить статистику за период."""
    response = requests.get(
        f"{API_BASE_URL}/api/v1/stats",
        params={"period": period}
    )
    response.raise_for_status()
    return response.json()

# Использование
stats = get_stats("day")
print(f"Total dialogs: {stats['general_stats']['total_dialogs']}")
print(f"Active users: {stats['general_stats']['active_users']}")
```

---

## Структура ответа

### StatsResponse

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
    {"time": "01:00", "messages": 8},
    ...
  ],
  "recent_dialogs": [
    {
      "user_display": "@john_doe",
      "message_count": 8,
      "last_active": "5 минут назад",
      "status": "active"
    },
    ...
  ],
  "top_users": [
    {
      "user_display": "@maria_s",
      "message_count": 156,
      "percentage": 100.0
    },
    ...
  ]
}
```

### Описание полей

#### general_stats
- `total_dialogs`: Общее количество диалогов
- `total_dialogs_change`: Процент изменения диалогов (±%)
- `active_users`: Количество активных пользователей
- `active_users_change`: Процент изменения пользователей (±%)
- `total_messages`: Общее количество сообщений
- `total_messages_change`: Процент изменения сообщений (±%)
- `avg_dialog_length`: Средняя длина диалога
- `avg_dialog_length_change`: Процент изменения средней длины (±%)

#### activity_chart
- `time`: Временная метка (формат зависит от period)
- `messages`: Количество сообщений в интервале

**Формат time:**
- `day`: "00:00", "01:00", ..., "23:00" (24 точки)
- `week`: "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс" (7 точек)
- `month`: "1", "2", "3", ..., "30" (30 точек)

#### recent_dialogs
- `user_display`: Отображаемое имя пользователя
- `message_count`: Количество сообщений в диалоге
- `last_active`: Относительное время последней активности
- `status`: Статус диалога (active/idle/inactive)

#### top_users
- `user_display`: Отображаемое имя пользователя
- `message_count`: Количество отправленных сообщений
- `percentage`: Процент активности относительно топа (0-100)

---

## Обработка ошибок

### 400 Bad Request - Невалидный period

```json
{
  "detail": "Invalid period value. Must be one of: day, week, month. Error: ..."
}
```

**Пример:**
```bash
curl "http://localhost:8000/api/v1/stats?period=invalid"
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## Тестирование API

### Через Makefile

```bash
# Запустить API сервер
make api-run

# В другом терминале: протестировать endpoints
make api-test

# Открыть документацию в браузере
make api-docs

# Запустить unit-тесты
make api-test-unit

# Проверить покрытие тестами
make api-coverage
```

### Через pytest

```bash
# Все тесты API
pytest tests/test_api_stats.py tests/test_mock_stat_collector.py -v

# Только интеграционные тесты
pytest tests/test_api_stats.py -v

# Только unit-тесты Mock collector
pytest tests/test_mock_stat_collector.py -v

# С coverage
pytest tests/test_api_stats.py -v --cov=src/api
```

---

## OpenAPI документация

### Swagger UI

Интерактивная документация с возможностью тестирования endpoints.

**URL:** http://localhost:8000/docs

**Функции:**
- Просмотр всех endpoints
- Интерактивное тестирование
- Просмотр схем данных
- Примеры запросов/ответов

### ReDoc

Альтернативная документация с красивым UI.

**URL:** http://localhost:8000/redoc

**Функции:**
- Детальное описание API
- Схемы данных
- Примеры
- Поиск по документации

### OpenAPI JSON

Спецификация API в формате JSON.

**URL:** http://localhost:8000/openapi.json

```bash
# Скачать спецификацию
curl http://localhost:8000/openapi.json > openapi.json
```

---

## CORS Configuration

API настроен для работы с frontend dev серверами:

**Разрешенные origins:**
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)
- `http://localhost:5174` (Vite alternative)
- `http://localhost:8080` (Alternative)

Если используется другой порт, добавьте его в `src/api_main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:YOUR_PORT",  # Добавьте ваш порт
    ],
    ...
)
```

---

## Производительность

### Время ответа

Mock API генерирует данные на лету, время ответа обычно < 50ms.

### Кеширование

В текущей реализации данные генерируются при каждом запросе. Для одинаковых периодов данные консистентны благодаря фиксированному seed.

---

## Troubleshooting

### API не запускается

**Проблема:** Порт 8000 уже занят

**Решение:** Измените порт при запуске
```bash
uvicorn src.api_main:app --port 8001
```

### CORS ошибки

**Проблема:** Frontend не может подключиться к API

**Решение:**
1. Проверьте что API запущен
2. Добавьте ваш frontend URL в CORS origins
3. Проверьте консоль браузера на ошибки

### Данные не обновляются

**Проблема:** При каждом запросе одинаковые данные

**Решение:** Это нормально для Mock API. Данные генерируются с фиксированным seed для консистентности. Разные периоды дают разные данные.

---

## Следующие шаги

1. **FE-S2:** Создание frontend проекта
2. **FE-S3:** Реализация dashboard с использованием этого API
3. **FE-S4:** Реализация AI-чата
4. **FE-S5:** Переход на реальный API с БД

---

## Дополнительные ресурсы

- [API Contract](./api-contract.md) - Подробное описание контракта
- [Dashboard Requirements](./dashboard-requirements.md) - Требования к dashboard
- [Frontend Roadmap](./frontend-roadmap.md) - План развития frontend

---

**Статус:** ✅ Mock API готов к использованию
**Версия API:** 1.0
**Последнее обновление:** 2025-10-17

