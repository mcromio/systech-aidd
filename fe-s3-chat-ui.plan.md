# План спринта FE-S3: Web UI для Telegram чата

> **Дата создания:** 17 октября 2025
> **Статус:** 📋 Запланирован
> **Продолжительность:** 3-5 дней

---

## 🎯 Цели спринта

1. Реализовать веб-интерфейс для просмотра и отправки сообщений Telegram бота
2. Создать Chat API для взаимодействия с базой данных диалогов
3. Обеспечить real-time или near-real-time обмен сообщениями
4. Предоставить удобный UX для администратора

---

## 📋 Контекст

### Существующая база

**Backend:**
- ✅ PostgreSQL с таблицами `users` и `messages`
- ✅ SQLAlchemy модели в `src/db/models.py`
- ✅ Repositories для работы с БД

**Frontend:**
- ✅ Next.js + TypeScript + shadcn/ui
- ✅ Структура проекта в `frontend/app/`
- ✅ Базовые компоненты (Header, Footer)

### Что нужно создать

**Backend API:**
- Endpoints для получения списка диалогов
- Endpoints для получения истории сообщений
- Endpoint для отправки сообщений от администратора

**Frontend UI:**
- Страница чата с двумя панелями (список диалогов + сообщения)
- Компоненты для отображения диалогов и сообщений
- Форма ввода и отправки сообщений

---

## 🔄 Итерации

### Iteration 1: Chat API - Базовые endpoints (Backend)

**Цель:** Создать API для получения диалогов и истории сообщений

**Задачи:**
1. Создать Chat API models (`src/api/chat_models.py`):
   - `Dialog` - информация о диалоге
   - `MessageItem` - сообщение в диалоге
   - `DialogsResponse` - список диалогов
   - `MessagesResponse` - история сообщений

2. Создать Chat API router (`src/api/chat_router.py`):
   - `GET /api/v1/chat/dialogs` - список всех диалогов
   - `GET /api/v1/chat/dialogs/{user_id}/messages` - история сообщений с пользователем

3. Интегрировать Chat router в `src/api_main.py`

4. Создать тесты для Chat API (`tests/test_chat_api.py`)

**Definition of Done:**
- ✅ Модели созданы и валидируются
- ✅ Endpoints возвращают данные из БД
- ✅ Тесты покрывают основные сценарии
- ✅ API документация в Swagger

---

### Iteration 2: Chat API - Отправка сообщений (Backend)

**Цель:** Реализовать отправку сообщений от администратора через API

**Задачи:**
1. Добавить endpoint для отправки сообщений:
   - `POST /api/v1/chat/dialogs/{user_id}/messages`
   - Request body: `SendMessageRequest { text: string }`
   - Response: созданное сообщение

2. Интегрироваться с Telegram Bot API:
   - Отправка сообщения пользователю через бота
   - Сохранение сообщения в БД

3. Обработка ошибок (пользователь не найден, бот заблокирован)

4. Тесты для отправки сообщений

**Definition of Done:**
- ✅ Endpoint отправляет сообщения в Telegram
- ✅ Сообщения сохраняются в БД
- ✅ Обработаны граничные случаи
- ✅ Тесты проходят

---

### Iteration 3: Frontend - Структура страницы и routing

**Цель:** Создать базовую структуру страницы чата

**Задачи:**
1. Создать страницу `/chat`:
   - `frontend/app/src/app/chat/page.tsx`
   - Layout: две панели (sidebar + main)

2. Создать типы для Chat API:
   - `frontend/app/src/lib/chat-types.ts`
   - Интерфейсы для Dialog, Message, etc.

3. Создать API client для Chat:
   - `frontend/app/src/lib/chat-api.ts`
   - Методы: `getDialogs()`, `getMessages(userId)`, `sendMessage(userId, text)`

4. Добавить navigation link в Header

**Definition of Done:**
- ✅ Страница `/chat` создана и доступна
- ✅ Layout с двумя панелями
- ✅ API client реализован
- ✅ Типы определены

---

### Iteration 4: Frontend - Список диалогов

**Цель:** Реализовать отображение списка диалогов

**Задачи:**
1. Создать компонент `DialogsList`:
   - `frontend/app/src/components/chat/dialogs-list.tsx`
   - Отображение списка диалогов с аватарами, именами, last message

2. Создать компонент `DialogItem`:
   - `frontend/app/src/components/chat/dialog-item.tsx`
   - Карточка диалога (аватар, имя, last message, timestamp)

3. Создать хук `useDialogs`:
   - `frontend/app/src/hooks/use-dialogs.ts`
   - Загрузка списка диалогов из API

4. Обработка состояний (loading, error, empty)

**Definition of Done:**
- ✅ Список диалогов отображается
- ✅ Компоненты styled и адаптивны
- ✅ Обработка loading/error states
- ✅ Клик на диалог выбирает его

---

### Iteration 5: Frontend - История сообщений

**Цель:** Реализовать отображение истории сообщений выбранного диалога

**Задачи:**
1. Создать компонент `MessagesList`:
   - `frontend/app/src/components/chat/messages-list.tsx`
   - Scroll container с сообщениями
   - Auto-scroll к последнему сообщению

2. Создать компонент `MessageBubble`:
   - `frontend/app/src/components/chat/message-bubble.tsx`
   - Bubble для сообщения (user vs assistant)
   - Timestamp, read status

3. Создать хук `useMessages`:
   - `frontend/app/src/hooks/use-messages.ts`
   - Загрузка истории сообщений для выбранного диалога

4. Обработка empty state (нет сообщений)

**Definition of Done:**
- ✅ История сообщений отображается
- ✅ Разные стили для user/assistant
- ✅ Auto-scroll работает
- ✅ Обработка loading/error states

---

### Iteration 6: Frontend - Отправка сообщений

**Цель:** Реализовать форму ввода и отправки сообщений

**Задачи:**
1. Создать компонент `MessageInput`:
   - `frontend/app/src/components/chat/message-input.tsx`
   - Textarea с кнопкой отправки
   - Enter для отправки (Shift+Enter для новой строки)

2. Интегрировать отправку с API:
   - Вызов `chatApi.sendMessage()`
   - Обновление списка сообщений после отправки
   - Optimistic update (добавить сообщение сразу)

3. Обработка ошибок отправки

4. Индикатор typing (опционально)

**Definition of Done:**
- ✅ Форма ввода работает
- ✅ Сообщения отправляются через API
- ✅ UI обновляется после отправки
- ✅ Обработка ошибок

---

### Iteration 7: Полировка и тестирование

**Цель:** Финализировать функционал, протестировать, исправить баги

**Задачи:**
1. UI/UX полировка:
   - Responsive design для мобильных
   - Loading states
   - Empty states
   - Error handling

2. Тестирование:
   - End-to-end тестирование основных сценариев
   - Проверка на разных разрешениях
   - Тестирование ошибок API

3. Документация:
   - Обновить `frontend/doc/README.md`
   - Добавить описание Chat API
   - Создать summary файл

4. Code review и рефакторинг

**Definition of Done:**
- ✅ Все компоненты responsive
- ✅ Нет критических багов
- ✅ Документация обновлена
- ✅ Code review пройден

---

## 📊 API Contract

### GET /api/v1/chat/dialogs

**Response:**
```json
{
  "dialogs": [
    {
      "user_id": 123456,
      "username": "john_doe",
      "first_name": "John",
      "last_name": "Doe",
      "last_message": {
        "text": "Hello!",
        "timestamp": "2025-10-17T12:00:00Z",
        "role": "user"
      },
      "unread_count": 2,
      "total_messages": 15
    }
  ]
}
```

### GET /api/v1/chat/dialogs/{user_id}/messages

**Query params:**
- `limit` (optional): default 50
- `offset` (optional): default 0

**Response:**
```json
{
  "user_id": 123456,
  "messages": [
    {
      "id": 1,
      "text": "Hello!",
      "role": "user",
      "timestamp": "2025-10-17T12:00:00Z",
      "metadata": {}
    },
    {
      "id": 2,
      "text": "Hi! How can I help?",
      "role": "assistant",
      "timestamp": "2025-10-17T12:00:05Z",
      "metadata": {}
    }
  ],
  "total": 15
}
```

### POST /api/v1/chat/dialogs/{user_id}/messages

**Request:**
```json
{
  "text": "Message from admin"
}
```

**Response:**
```json
{
  "id": 3,
  "text": "Message from admin",
  "role": "assistant",
  "timestamp": "2025-10-17T12:05:00Z",
  "sent_to_telegram": true
}
```

---

## 🧰 Технологический стек

**Backend:**
- FastAPI (endpoint handlers)
- SQLAlchemy (БД queries)
- aiogram (отправка в Telegram)
- Pydantic (модели)

**Frontend:**
- Next.js 15 + React
- TypeScript
- shadcn/ui компоненты
- Tailwind CSS
- React hooks (useState, useEffect)

---

## 📝 Makefile команды

Добавить в `Makefile`:

```makefile
# Chat API
.PHONY: chat-api-test
chat-api-test:
	uv run pytest tests/test_chat_api.py -v

.PHONY: chat-run
chat-run: api-run
	@echo "Chat API доступен на http://localhost:8000/api/v1/chat"
```

---

## ✅ Definition of Done (весь спринт)

- [ ] Chat API реализован и протестирован
- [ ] Frontend чата работает и отображает данные
- [ ] Можно просматривать список диалогов
- [ ] Можно просматривать историю сообщений
- [ ] Можно отправлять сообщения от администратора
- [ ] Сообщения доставляются в Telegram
- [ ] UI адаптивен (responsive)
- [ ] Обработаны loading/error states
- [ ] Документация обновлена
- [ ] Тесты покрывают основной функционал
- [ ] Нет критических багов
- [ ] Code review пройден

---

## 🔗 Зависимости

**Предварительные требования:**
- ✅ FE-S1: Mock API завершен (API структура понятна)
- ✅ FE-S2: Frontend проект инициализирован
- ✅ БД с таблицами users и messages

**Блокеры:**
- Отсутствуют

---

## 📚 Референсы

**UI/UX:**
- Telegram Web (https://web.telegram.org/) - референс по UX
- WhatsApp Web - альтернативный референс
- shadcn/ui Chat примеры

**API Design:**
- REST API Best Practices
- FastAPI документация
- OpenAPI спецификация

---

## 🎓 Примечания

### Опциональные улучшения (не в этом спринте)

- WebSocket для real-time обновлений
- Поиск по диалогам и сообщениям
- Фильтры и сортировка диалогов
- Markdown поддержка в сообщениях
- Отправка файлов/изображений
- Уведомления о новых сообщениях
- Pagination для больших историй

### Технические заметки

- Используем polling для обновления (refresh каждые N секунд) вместо WebSocket (для простоты)
- Admin отправляет сообщения от имени бота
- Сообщения сохраняются в БД с role="assistant"

---

**Версия плана:** 1.0
**Создан:** 17 октября 2025
**Статус:** 📋 Готов к выполнению

