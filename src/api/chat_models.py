"""Pydantic модели для Chat API."""

from datetime import datetime

from pydantic import BaseModel, Field


class LastMessage(BaseModel):
    """Последнее сообщение в диалоге."""

    text: str = Field(..., description="Текст сообщения")
    timestamp: datetime = Field(..., description="Время отправки")
    role: str = Field(..., description="Роль отправителя (user/assistant)")


class Dialog(BaseModel):
    """Информация о диалоге с пользователем."""

    user_id: int = Field(..., description="Telegram ID пользователя")
    username: str | None = Field(None, description="Username пользователя")
    first_name: str | None = Field(None, description="Имя пользователя")
    last_name: str | None = Field(None, description="Фамилия пользователя")
    last_message: LastMessage | None = Field(None, description="Последнее сообщение")
    unread_count: int = Field(0, description="Количество непрочитанных сообщений")
    total_messages: int = Field(0, description="Всего сообщений в диалоге")


class DialogsResponse(BaseModel):
    """Ответ со списком диалогов."""

    dialogs: list[Dialog] = Field(..., description="Список диалогов")


class MessageItem(BaseModel):
    """Сообщение в диалоге."""

    id: int = Field(..., description="ID сообщения")
    text: str = Field(..., description="Текст сообщения")
    role: str = Field(..., description="Роль отправителя (user/assistant)")
    timestamp: datetime = Field(..., description="Время отправки")


class MessagesResponse(BaseModel):
    """Ответ с историей сообщений."""

    user_id: int = Field(..., description="Telegram ID пользователя")
    messages: list[MessageItem] = Field(..., description="Список сообщений")
    total: int = Field(..., description="Всего сообщений")


class SendMessageRequest(BaseModel):
    """Запрос на отправку сообщения."""

    text: str = Field(..., min_length=1, max_length=4096, description="Текст сообщения")


class SendMessageResponse(BaseModel):
    """Ответ после отправки сообщения."""

    id: int = Field(..., description="ID созданного сообщения")
    text: str = Field(..., description="Текст сообщения")
    role: str = Field("assistant", description="Роль (всегда assistant)")
    timestamp: datetime = Field(..., description="Время отправки")
    sent_to_telegram: bool = Field(..., description="Отправлено ли в Telegram")
