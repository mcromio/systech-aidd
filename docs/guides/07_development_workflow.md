# 🔄 Development Workflow - Процессы разработки

> Как работать над проектом от задачи до коммита

---

## 🎯 Общий workflow

```mermaid
graph LR
    A[📋 Задача] --> B[🔄 TDD: Write Test]
    B --> C[🔴 RED: Test Fails]
    C --> D[💻 Write Code]
    D --> E[🟢 GREEN: Test Passes]
    E --> F[🔵 REFACTOR: Clean Code]
    F --> G[✅ Lint + Format]
    G --> H[📝 Commit]
    H --> I[🔁 Code Review]

    style A fill:#2196F3,stroke:#1565C0,color:#fff
    style C fill:#F44336,stroke:#C62828,color:#fff
    style E fill:#4CAF50,stroke:#2E7D32,color:#fff
    style F fill:#2196F3,stroke:#1565C0,color:#fff
    style H fill:#FF9800,stroke:#E65100,color:#fff
```

---

## 📝 Выбор задачи

### Из tasklist.md

```markdown
## Iteration 8: Полная интеграция
- [ ] Интеграционные тесты
- [ ] E2E сценарии
```

**Обновить статус:**
```markdown
- [x] Интеграционные тесты  ← Отметить когда завершено
```

---

## 🧪 TDD подход (RED → GREEN → REFACTOR)

### 🔴 RED Phase: Написать падающий тест

```python
# tests/test_my_feature.py
import pytest

def test_new_feature():
    """Тест новой фичи."""
    result = my_new_function()
    assert result == "expected"
```

**Запустить:**
```bash
pytest tests/test_my_feature.py -v
# Output: FAILED - my_new_function не существует ❌
```

---

### 🟢 GREEN Phase: Минимальный код для прохождения

```python
# src/my_module.py
def my_new_function() -> str:
    """Новая функция."""
    return "expected"
```

**Запустить:**
```bash
pytest tests/test_my_feature.py -v
# Output: PASSED ✅
```

---

### 🔵 REFACTOR Phase: Улучшить код

```python
# src/my_module.py
def my_new_function() -> str:
    """
    Новая функция.

    Returns:
        Результат работы функции
    """
    result = _compute_result()
    return result

def _compute_result() -> str:
    """Вычислить результат."""
    return "expected"
```

**Убедиться что тесты остались зелеными:**
```bash
pytest tests/test_my_feature.py -v
# Output: PASSED ✅
```

---

## 📐 Conventions - Правила кодирования

### Type Hints (обязательно!)

```python
# ✅ Правильно
def process_message(user_id: int, text: str) -> str | None:
    pass

# ❌ Неправильно
def process_message(user_id, text):
    pass
```

---

### Docstrings (на русском)

```python
# ✅ Правильно
async def handle_start(self, message: Message) -> None:
    """
    Обработка команды /start.

    Args:
        message: Сообщение от пользователя
    """
    pass

# ❌ Неправильно (без docstring)
async def handle_start(self, message: Message) -> None:
    pass
```

---

### Логирование (только logging)

```python
import logging

logger = logging.getLogger(__name__)

# ✅ Правильно
logger.info(f"Сообщение от пользователя {user_id}")
logger.error(f"Ошибка: {e}", exc_info=True)

# ❌ Неправильно
print("Something happened")
```

---

### Короткие методы (≤ 40 строк)

```python
# ✅ Правильно - разбить на методы
async def handle_message(self, message: Message):
    user_id = self._get_user_id(message)
    context = self._get_context(user_id)
    response = await self._get_llm_response(context)
    await self._send_response(message, response)

# ❌ Неправильно - 100+ строк в одном методе
async def handle_message(self, message: Message):
    # ... 100 строк ...
```

---

## 🧹 Линтинг и форматирование

### Перед коммитом (обязательно!)

```bash
# 1. Форматирование
make format
# Output: Reformatted X files

# 2. Линтинг (ruff)
make lint
# Output: All checks passed!

# 3. Type checking (mypy)
make type-check
# Output: Success: no issues found

# 4. Тесты
make test
# Output: 55 passed
```

---

### Автоматическая проверка

```bash
# Запустить всё сразу
make check
# Выполнит: lint + type-check + test
```

---

## ✅ Definition of Done

Задача завершена когда:

- [ ] Код написан
- [ ] Type hints везде
- [ ] Docstrings на русском
- [ ] Логирование через logging
- [ ] Тесты написаны
- [ ] Тесты проходят (`make test`)
- [ ] Линтер проходит (`make lint`)
- [ ] Type checker проходит (`make type-check`)
- [ ] Coverage не упал
- [ ] Код отревьюен
- [ ] Документация обновлена (если нужно)

---

## 📝 Git workflow

### Branch naming

```bash
# Feature
git checkout -b feature/add-weather-tool

# Bugfix
git checkout -b bugfix/fix-context-limit

# Refactor
git checkout -b refactor/split-llm-client

# TechDebt
git checkout -b techdebt/add-mypy
```

---

### Commit message format

```bash
git commit -m "feat(tools): добавить WeatherTool

- Создан WeatherTool класс
- Добавлена интеграция с OpenWeatherMap API
- Добавлены тесты test_weather_tool.py
- Coverage: 85%

Closes #42"
```

**Типы коммитов:**
- `feat` - новая фича
- `fix` - исправление бага
- `refactor` - рефакторинг
- `test` - добавление тестов
- `docs` - документация
- `chore` - служебные изменения

---

### Что коммитить

```bash
# ✅ Коммитить
git add src/
git add tests/
git add docs/
git add pyproject.toml

# ❌ НЕ коммитить
# .env (секреты)
# __pycache__/ (кэш)
# .pytest_cache/ (кэш тестов)
# coverage.json (генерируется)
```

---

## 👀 Code Review чек-лист

### Для автора (перед PR)

- [ ] Все тесты проходят
- [ ] Линтер проходит
- [ ] Type checker проходит
- [ ] Coverage не упал
- [ ] Код самодокументируемый
- [ ] Нет дублирования (DRY)
- [ ] Следует conventions.md
- [ ] Обновлена документация

---

### Для ревьюера

**Проверить:**

1. **Архитектура:**
   - [ ] Single Responsibility соблюден
   - [ ] Нет избыточных абстракций
   - [ ] Зависимости явные

2. **Код:**
   - [ ] Type hints везде
   - [ ] Docstrings на русском
   - [ ] Методы < 40 строк
   - [ ] Нет магических чисел

3. **Тесты:**
   - [ ] Покрыта новая функциональность
   - [ ] Тесты понятные
   - [ ] Используются моки где нужно

4. **Безопасность:**
   - [ ] Нет хардкода секретов
   - [ ] Валидация входных данных
   - [ ] Обработка ошибок

---

## 🔧 Рефакторинг

### Когда рефакторить

- Код дублируется > 2 раз → вынести в метод
- Метод > 40 строк → разбить
- Класс делает > 1 задачи → разделить
- Магические числа → в Config
- Сложная логика → упростить

---

### Процесс рефакторинга

```bash
# 1. Убедиться что тесты проходят
make test
# Output: 55 passed ✅

# 2. Рефакторинг кода
# (изменения...)

# 3. Убедиться что тесты остались зелеными
make test
# Output: 55 passed ✅

# 4. Запустить линтер
make lint
# Output: All checks passed!

# 5. Закоммитить
git commit -m "refactor: упростить tool calling loop"
```

---

## 🐛 Debugging

### Локальная отладка

```python
# Добавить breakpoint
import pdb; pdb.set_trace()

# Или в VS Code/PyCharm - поставить точку останова
```

**Запустить с отладкой:**
```bash
python -m src.main
# Выполнение остановится на breakpoint
```

---

### Логирование для отладки

```python
# Временно переключить на DEBUG
# .env
LOG_LEVEL=DEBUG

# Перезапустить
make run

# Вывод:
# DEBUG | src.llm_client | Запрос к OpenAI: 3 сообщения
# DEBUG | src.llm_client | Получен ответ: 150 токенов
```

---

## 📊 Coverage

### Проверить coverage

```bash
make test
# Output:
# ...
# TOTAL    341    437    78%
```

**Цель:** 85%+

---

### Найти непокрытые строки

```bash
pytest --cov=src --cov-report=term-missing
# Output:
# src/bot.py       28      28     0%   23-65
#                                      ↑ строки без покрытия
```

---

## 🔁 Итеративная разработка

### Малые итерации

```
Плохо: Написать весь функционал сразу → 1 большой PR
Хорошо: Разбить на итерации → несколько маленьких PR
```

**Пример:**
```
Iter 1: Базовая структура + тесты
Iter 2: Интеграция с API + тесты
Iter 3: Обработка ошибок + тесты
Iter 4: Рефакторинг
```

---

## 📚 Дополнительно

**Conventions:** [../conventions.md](../conventions.md)
**Vision:** [../vision.md](../vision.md)
**Тестирование:** [08_testing_guide.md](08_testing_guide.md)
**Troubleshooting:** [10_troubleshooting.md](10_troubleshooting.md)






