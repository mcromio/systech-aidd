# ADR-002: Выбор SQLAlchemy ORM

**Дата**: 16 октября 2025
**Статус**: Принято
**Авторы**: Development Team

## Контекст

Для работы с PostgreSQL необходимо выбрать способ взаимодействия с базой данных. Основной выбор между использованием ORM (Object-Relational Mapping) и чистым SQL.

## Рассматриваемые варианты

### 1. Чистый SQL (asyncpg/aiosqlite)
**Плюсы:**
- Максимальная производительность
- Полный контроль над SQL запросами
- Нет магии и скрытой логики
- Меньше зависимостей
- Простота отладки (видим SQL напрямую)

**Минусы:**
- Больше boilerplate кода
- Ручное управление моделями и маппингом
- Дублирование SQL запросов
- Нет автоматической валидации типов
- Сложнее рефакторинг схемы

### 2. SQLAlchemy Core
**Плюсы:**
- SQL-подобный API (expression language)
- Хорошая производительность
- Меньше магии чем ORM
- Гибкость в запросах

**Минусы:**
- Нужно писать больше кода чем в ORM
- Нет автоматического управления отношениями
- Ручное определение моделей

### 3. SQLAlchemy ORM
**Плюсы:**
- Декларативные модели (DRY)
- Автоматический маппинг Python ↔ SQL
- Управление отношениями (relationships)
- Type hints и автодополнение в IDE
- Валидация на уровне ORM
- Легкий рефакторинг схемы
- Миграции через Alembic
- Богатая экосистема

**Минусы:**
- Дополнительный слой абстракции
- Потенциальные проблемы с производительностью (N+1)
- Магия и неявное поведение
- Кривая обучения

### 4. Другие ORM (Tortoise ORM, Piccolo, etc.)
**Плюсы:**
- Более простой API
- Современный async-first дизайн

**Минусы:**
- Меньшее комьюнити
- Меньше инструментов (миграции)
- Менее зрелые решения

## Решение

**Выбран SQLAlchemy 2.0 ORM (async mode)**

## Обоснование

1. **Стандарт индустрии**: SQLAlchemy - де-факто стандарт для Python проектов с БД

2. **SQLAlchemy 2.0**: Современная версия с полной поддержкой async/await
   ```python
   async with async_session() as session:
       result = await session.execute(select(User))
   ```

3. **Декларативные модели**:
   ```python
   class Message(Base):
       __tablename__ = "messages"
       id = Column(Integer, primary_key=True)
       content = Column(Text, nullable=False)
       created_at = Column(DateTime, default=func.now())
   ```
   - Один источник правды для схемы
   - Type hints для IDE
   - Валидация типов

4. **Отношения**: Автоматическое управление FK и relationships
   ```python
   user = relationship("User", back_populates="messages")
   ```

5. **Миграции через Alembic**:
   - Автогенерация миграций из моделей
   - Версионирование схемы
   - Up/down миграции

6. **Repository Pattern**: ORM идеально сочетается с Repository
   ```python
   class MessageRepository:
       async def create_message(self, user_id: int, content: str):
           message = Message(user_id=user_id, content=content)
           self.session.add(message)
           await self.session.commit()
   ```

7. **Тестируемость**: Легко мокировать для unit-тестов

8. **Экосистема**:
   - Отличная документация
   - Большое комьюнити
   - Интеграции с FastAPI, Flask и т.д.

9. **Безопасность**: Защита от SQL injection из коробки

10. **Будущее расширение**: Легко добавлять новые таблицы и отношения

## Последствия

### Положительные
- ✅ Быстрая разработка (меньше boilerplate)
- ✅ Type safety и автодополнение
- ✅ Легкий рефакторинг схемы
- ✅ Готовые миграции (Alembic)
- ✅ Стандартизация кода

### Отрицательные
- ⚠️ Дополнительная зависимость (~1.5MB)
- ⚠️ Нужно понимать SQLAlchemy API
- ⚠️ Потенциальные проблемы с производительностью (mitigation: query optimization)

### Риски и митигации

- **Риск**: N+1 проблема при загрузке отношений
  **Митигация**:
  - Использовать `selectinload()` / `joinedload()`
  - Мониторинг количества запросов в тестах
  - Логирование SQL в dev режиме (`echo=True`)

- **Риск**: Неоптимальные запросы из-за автоматической генерации
  **Митигация**:
  - Raw SQL для сложных запросов через `text()`
  - Профилирование запросов
  - EXPLAIN ANALYZE в production

- **Риск**: Магия и неявное поведение
  **Митигация**:
  - Явное управление транзакциями
  - Отключение autoflush где нужно
  - Документирование поведения в docstrings

## Компромиссы

Мы **жертвуем**:
- Максимальной производительностью (~5-10% overhead)
- Полным контролем над SQL

Мы **получаем**:
- Скорость разработки (+50% быстрее)
- Maintainability кода
- Готовую систему миграций
- Type safety

## План оптимизации (если потребуется)

1. **Phase 1** (текущая): SQLAlchemy ORM для всего
2. **Phase 2** (если есть bottleneck): Гибридный подход
   - ORM для CRUD операций
   - Raw SQL для сложных аналитических запросов
3. **Phase 3** (если критична производительность): asyncpg для hot path

## Примеры использования

```python
# Создание сообщения
async def create_message(session: AsyncSession, user_id: int, content: str):
    message = Message(
        user_id=user_id,
        role="user",
        content=content,
        content_length=len(content)
    )
    session.add(message)
    await session.commit()
    return message

# Получение истории (с фильтром soft delete)
async def get_history(session: AsyncSession, user_id: int, limit: int):
    stmt = (
        select(Message)
        .where(Message.user_id == user_id, Message.is_deleted == False)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

# Soft delete
async def soft_delete_messages(session: AsyncSession, user_id: int):
    stmt = (
        update(Message)
        .where(Message.user_id == user_id, Message.is_deleted == False)
        .values(is_deleted=True, deleted_at=func.now())
    )
    await session.execute(stmt)
    await session.commit()
```

## Ссылки

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [SQLAlchemy async tutorial](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Best practices for SQLAlchemy](https://docs.sqlalchemy.org/en/20/faq/performance.html)

