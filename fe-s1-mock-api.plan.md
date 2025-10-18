<!-- 2d4090c2-04ad-4dcf-8a3b-ebc1bc8fe3a0 285e4c53-d893-4bf8-91b3-9f3c09e4fbdc -->
# Sprint Plan: FE-S1 - Mock API для статистики диалогов

## Цели спринта

1. Сформировать функциональные требования к дашборду на основе референса
2. Спроектировать REST API контракт для фронтенда (один метод GET /stats)
3. Реализовать интерфейс StatCollector с Mock реализацией
4. Создать независимый API сервер с автоматической документацией
5. Обеспечить возможность разработки фронтенда без зависимости от БД

## Итерации

### Iteration 1: Анализ референса и требования к дашборду (1 день)

**Цель:** Определить функциональные требования к дашборду статистики на основе референса

**Задачи:**

- Изучить референс дашборда (front-reference.png, shadcn/ui blocks)
- Определить список метрик для отображения:
  - Общая статистика (всего диалогов, активных пользователей, средняя длина)
  - График активности по времени (данные для визуализации)
  - Список последних диалогов с метаданными
  - Топ пользователей по активности
- Проанализировать существующую структуру БД (users, messages таблицы)
- Создать документ `frontend/doc/dashboard-requirements.md` с функциональными требованиями
- Определить структуру данных для каждой метрики

**Критерий готовности:**

```bash
cat frontend/doc/dashboard-requirements.md
# Документ содержит:
# - Список всех метрик
# - Описание структуры данных
# - Примеры значений
```

---

### Iteration 2: Проектирование API контракта (1 день)

**Цель:** Спроектировать REST API контракт и интерфейс StatCollector

**Задачи:**

- Создать документ `frontend/doc/api-contract.md` с описанием API
- Спроектировать endpoint: `GET /api/v1/stats?period=day|week|month`
- Определить структуру JSON ответа со всеми метриками
- Создать Pydantic модели для ответа API:
  - `StatsResponse` (общая структура)
  - `GeneralStats` (общие метрики)
  - `ActivityDataPoint` (точка на графике)
  - `DialogInfo` (информация о диалоге)
  - `UserActivity` (активность пользователя)
- Спроектировать интерфейс `StatCollector` (Protocol):
  - Метод `get_stats(period: str) -> StatsResponse`
- Создать примеры JSON ответа для каждого периода

**Критерий готовности:**

```bash
cat frontend/doc/api-contract.md
# Содержит полное описание API с примерами JSON

cat src/api/models.py
# Содержит Pydantic модели для всех структур данных
```

---

### Iteration 3: Настройка FastAPI и структура проекта (1 день)

**Цель:** Настроить FastAPI, создать структуру API проекта

**Задачи:**

- Добавить FastAPI в `pyproject.toml` dependencies: `fastapi>=0.115.0`, `uvicorn>=0.31.0`
- Создать структуру директорий:
  ```
  src/api/
  ├── __init__.py
  ├── models.py       # Pydantic модели
  ├── collector.py    # StatCollector Protocol
  ├── mock.py         # MockStatCollector
  └── router.py       # FastAPI router с endpoints
  ```

- Создать `src/api_main.py` как entrypoint для API сервера
- Настроить FastAPI приложение с CORS (для разработки фронтенда)
- Настроить автоматическую генерацию OpenAPI документации
- Создать базовый endpoint `/health` для проверки работоспособности

**Критерий готовности:**

```bash
uv sync
# FastAPI установлен

python -m src.api_main &
curl http://localhost:8000/health
# Output: {"status": "ok"}

curl http://localhost:8000/docs
# OpenAPI документация доступна
```

---

### Iteration 4: Mock StatCollector с тестовыми данными (1-2 дня)

**Цель:** Реализовать Mock реализацию StatCollector с реалистичными данными

**Задачи:**

- Создать Protocol `StatCollector` в `src/api/collector.py`
- Реализовать `MockStatCollector` в `src/api/mock.py`:
  - Генерация общей статистики (случайные но реалистичные значения)
  - Генерация данных для графика активности (почасовая/дневная/месячная)
  - Генерация списка последних 10 диалогов с метаданными
  - Генерация топ-5 пользователей по активности
- Использовать `random` для генерации данных с seed для воспроизводимости
- Добавить логику изменения данных в зависимости от period (day/week/month)
- Сделать данные реалистичными (даты, имена, активность по времени суток)
- Написать unit-тесты для MockStatCollector (`tests/test_mock_stat_collector.py`)

**Критерий готовности:**

```python
from src.api.collector import StatCollector
from src.api.mock import MockStatCollector

collector: StatCollector = MockStatCollector()
stats = collector.get_stats("day")
assert stats.general_stats.total_dialogs > 0
assert len(stats.activity_chart) > 0
assert len(stats.recent_dialogs) <= 10
```

---

### Iteration 5: API endpoint и документация (1 день)

**Цель:** Реализовать API endpoint с полной документацией

**Задачи:**

- Создать FastAPI router в `src/api/router.py`
- Реализовать endpoint `GET /api/v1/stats`:
  - Query параметр `period` с валидацией (day/week/month)
  - Использование MockStatCollector для получения данных
  - Правильные HTTP коды ответа
  - Обработка ошибок (400 для невалидного period)
- Добавить подробные docstrings для OpenAPI документации
- Добавить примеры ответов в OpenAPI (examples)
- Настроить теги и описания для группировки endpoints
- Написать интеграционные тесты (`tests/test_api_stats.py`)

**Критерий готовности:**

```bash
# Запуск API
python -m src.api_main &

# Тестирование endpoint
curl "http://localhost:8000/api/v1/stats?period=day" | jq .
# Output: корректный JSON с данными

# Проверка валидации
curl "http://localhost:8000/api/v1/stats?period=invalid"
# Output: 400 Bad Request с описанием ошибки

# OpenAPI документация
open http://localhost:8000/docs
# Полная документация с примерами
```

---

### Iteration 6: Команды Makefile и финальное тестирование (1 день)

**Цель:** Добавить команды для работы с API в Makefile и финальное тестирование

**Задачи:**

- Добавить команды в Makefile:
  ```makefile
  api-run: ## Запустить Mock API сервер
  api-test: ## Тестировать API endpoints
  api-docs: ## Открыть API документацию
  api-test-unit: ## Unit-тесты API модулей
  api-coverage: ## Coverage API модулей
  ```

- Реализовать `api-run`: запуск uvicorn с hot-reload
- Реализовать `api-test`: curl команды для всех endpoints и periods
- Создать документ `frontend/doc/api-usage.md` с примерами использования
- Написать полный набор тестов:
  - Unit-тесты для MockStatCollector
  - Интеграционные тесты для API endpoints
  - Тесты валидации параметров
- Проверить coverage тестов (>= 85% для api модулей)
- Создать примеры запросов к API (curl, JavaScript, React, Vue, Python)
- Актуализировать `frontend/doc/frontend-roadmap.md` после выполнения спринта
- Добавить ссылку на план в таблицу спринтов

**Критерий готовности:**

```bash
# Команды работают
make api-run
# API запущен на http://localhost:8000

make api-test
# Все тесты проходят (day/week/month periods)

make test
# Все unit и интеграционные тесты проходят
# Coverage API модулей >= 85%

cat frontend/doc/api-usage.md
# Документ с примерами использования API (curl, JS, React, Vue, Python)

cat frontend/doc/frontend-roadmap.md
# FE-S1 помечен как "✅ Завершен" со ссылкой на план
```

---

## Definition of Done

Спринт считается завершенным, если:

1. ✅ Создан документ с функциональными требованиями к дашборду
2. ✅ Спроектирован и документирован REST API контракт
3. ✅ Реализован Protocol StatCollector и Mock реализация
4. ✅ API сервер работает независимо от основного бота
5. ✅ OpenAPI документация генерируется автоматически
6. ✅ Все endpoints возвращают корректные данные
7. ✅ Добавлены команды в Makefile (api-run, api-test, api-docs, api-test-unit, api-coverage)
8. ✅ Написаны unit и интеграционные тесты (coverage >= 85%)
9. ✅ Создана документация по использованию API с примерами (curl, JS, React, Vue, Python)
10. ✅ Type hints везде, docstrings на русском
11. ✅ Линтер и type-checker проходят без ошибок
12. ✅ Frontend roadmap обновлен со статусом спринта и ссылкой на план

---

## Зависимости

- FastAPI >= 0.115.0
- uvicorn >= 0.31.0
- httpx >= 0.27.0 (для тестов)
- Существующие Pydantic модели (используем для валидации)

---

## Файлы для создания

1. `frontend/doc/dashboard-requirements.md` - требования к дашборду
2. `frontend/doc/api-contract.md` - описание API контракта
3. `frontend/doc/api-usage.md` - примеры использования
4. `src/api/__init__.py` - API модуль
5. `src/api/models.py` - Pydantic модели ответов
6. `src/api/collector.py` - StatCollector Protocol
7. `src/api/mock.py` - MockStatCollector реализация
8. `src/api/router.py` - FastAPI router
9. `src/api_main.py` - entrypoint для API сервера
10. `tests/test_mock_stat_collector.py` - unit-тесты Mock
11. `tests/test_api_stats.py` - интеграционные тесты API
12. `frontend/FE_S1_IMPLEMENTATION_SUMMARY.md` - итоговая сводка спринта

---

## Обновления существующих файлов

1. `pyproject.toml` - добавить FastAPI, uvicorn, httpx
2. `Makefile` - добавить команды api-run, api-test, api-docs, api-test-unit, api-coverage
3. `frontend/doc/frontend-roadmap.md` - обновить статус FE-S1 и добавить ссылку на план

---

## Проверка консистентности плана

### ✅ Соответствие плана реализации

| Пункт плана | Статус | Проверка |
|-------------|--------|----------|
| 6 итераций запланировано | ✅ | Все 6 итераций выполнены |
| 12 файлов создано | ✅ | Все файлы созданы |
| 3 файла обновлено | ✅ | pyproject.toml, Makefile, frontend-roadmap.md |
| Definition of Done (12 пунктов) | ✅ | Все пункты выполнены |
| Coverage >= 85% | ✅ | Достигнуто 94% |
| Все тесты проходят | ✅ | 46/46 тестов |
| Линтер без ошибок | ✅ | ruff: all checks passed |
| Type checker без ошибок | ✅ | mypy: success |

### ✅ Согласованность документации

| Документ | Ссылки консистентны | Структура соответствует плану |
|----------|---------------------|------------------------------|
| dashboard-requirements.md | ✅ | ✅ Все метрики описаны |
| api-contract.md | ✅ | ✅ Endpoint и модели документированы |
| api-usage.md | ✅ | ✅ Примеры для всех платформ |
| frontend-roadmap.md | ✅ | ✅ Статус обновлен, ссылка на план |

### ✅ Технические требования

| Требование | Статус | Результат |
|------------|--------|-----------|
| FastAPI >= 0.115.0 | ✅ | 0.119.0 установлен |
| uvicorn >= 0.31.0 | ✅ | 0.37.0 установлен |
| httpx >= 0.27.0 | ✅ | Установлен в dev dependencies |
| OpenAPI документация | ✅ | Swagger UI + ReDoc работают |
| CORS настроен | ✅ | Для localhost:3000/5173/5174/8080 |
| Type hints 100% | ✅ | Mypy проходит без ошибок |
| Docstrings на русском | ✅ | Все функции документированы |

---

## To-dos

- [x] Iteration 1: Анализ референса и формирование требований к дашборду
- [x] Iteration 2: Проектирование API контракта и интерфейса StatCollector
- [x] Iteration 3: Настройка FastAPI и структура проекта
- [x] Iteration 4: Реализация Mock StatCollector с тестовыми данными
- [x] Iteration 5: API endpoint и документация
- [x] Iteration 6: Команды Makefile и финальное тестирование
- [x] Актуализация frontend-roadmap.md после выполнения спринта
- [x] Добавление ссылки на план в таблицу спринтов в frontend-roadmap.md
- [x] Создание примеров запросов к API для тестирования (curl, JavaScript, React, Vue, Python)

---

## Итоговый статус

**✅ Спринт FE-S1 успешно завершен!**

**Метрики:**
- Тесты: 46/46 ✅ (100% passed)
- Coverage: 94% ✅ (требовалось ≥85%)
- Линтер: 0 errors ✅
- Type checker: 0 issues ✅

**Результат:**
Mock Stats API полностью готов для независимой разработки frontend dashboard. API предоставляет реалистичные тестовые данные, автоматическую документацию, высокое качество кода и отличный DX (developer experience).

**Frontend команда может начинать разработку UI! 🚀**

---

*План создан: 2025-10-17*
*Последнее обновление: 2025-10-17*
*Статус: ✅ Завершен*

