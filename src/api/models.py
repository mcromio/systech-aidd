"""Pydantic модели для Stats API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GeneralStats(BaseModel):
    """
    Общая статистика за период.

    Attributes:
        total_dialogs: Общее количество уникальных диалогов
        total_dialogs_change: Процент изменения относительно предыдущего периода
        active_users: Количество активных пользователей
        active_users_change: Процент изменения активных пользователей
        total_messages: Общее количество сообщений
        total_messages_change: Процент изменения сообщений
        avg_dialog_length: Среднее количество сообщений на диалог
        avg_dialog_length_change: Процент изменения средней длины
    """

    total_dialogs: int = Field(..., ge=0, description="Общее количество диалогов")
    total_dialogs_change: float = Field(
        ..., description="Процент изменения диалогов относительно предыдущего периода"
    )

    active_users: int = Field(..., ge=0, description="Количество активных пользователей")
    active_users_change: float = Field(..., description="Процент изменения активных пользователей")

    total_messages: int = Field(..., ge=0, description="Общее количество сообщений")
    total_messages_change: float = Field(..., description="Процент изменения сообщений")

    avg_dialog_length: float = Field(..., ge=0, description="Средняя длина диалога")
    avg_dialog_length_change: float = Field(..., description="Процент изменения средней длины")


class ActivityDataPoint(BaseModel):
    """
    Точка данных для графика активности.

    Attributes:
        time: Временная метка (формат зависит от периода)
        messages: Количество сообщений в этом интервале
    """

    time: str = Field(..., description="Временная метка (формат зависит от периода)")
    messages: int = Field(..., ge=0, description="Количество сообщений")


class DialogInfo(BaseModel):
    """
    Информация о диалоге пользователя.

    Attributes:
        user_display: Отображаемое имя пользователя (@username или FirstName LastName)
        message_count: Количество сообщений в диалоге
        last_active: Относительное время последней активности
        status: Статус диалога (active/idle/inactive)
    """

    user_display: str = Field(
        ..., description="Отображаемое имя пользователя (@username или FirstName LastName)"
    )
    message_count: int = Field(..., ge=0, description="Количество сообщений в диалоге")
    last_active: str = Field(..., description="Относительное время последней активности")
    status: Literal["active", "idle", "inactive"] = Field(
        ..., description="Статус диалога (active/idle/inactive)"
    )


class UserActivity(BaseModel):
    """
    Активность пользователя (для топа).

    Attributes:
        user_display: Отображаемое имя пользователя
        message_count: Общее количество отправленных сообщений
        percentage: Процент активности относительно самого активного (0-100)
    """

    user_display: str = Field(..., description="Отображаемое имя пользователя")
    message_count: int = Field(..., ge=0, description="Общее количество сообщений")
    percentage: float = Field(..., ge=0, le=100, description="Процент активности относительно топа")


class StatsResponse(BaseModel):
    """
    Корневая модель ответа API статистики.

    Attributes:
        period: Период анализа (day/week/month)
        generated_at: Timestamp генерации данных
        general_stats: Общая статистика
        activity_chart: Данные для графика активности
        recent_dialogs: Список последних диалогов
        top_users: Топ пользователей по активности
    """

    period: Literal["day", "week", "month"] = Field(..., description="Период анализа")
    generated_at: datetime = Field(..., description="Timestamp генерации данных")
    general_stats: GeneralStats = Field(..., description="Общая статистика")
    activity_chart: list[ActivityDataPoint] = Field(
        ..., description="Данные для графика активности"
    )
    recent_dialogs: list[DialogInfo] = Field(
        ..., max_length=10, description="Список последних диалогов (макс 10)"
    )
    top_users: list[UserActivity] = Field(
        ..., max_length=5, description="Топ пользователей по активности (макс 5)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
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
                        "avg_dialog_length_change": -2.1,
                    },
                    "activity_chart": [
                        {"time": "00:00", "messages": 12},
                        {"time": "01:00", "messages": 8},
                        {"time": "02:00", "messages": 5},
                    ],
                    "recent_dialogs": [
                        {
                            "user_display": "@john_doe",
                            "message_count": 8,
                            "last_active": "5 минут назад",
                            "status": "active",
                        },
                        {
                            "user_display": "Иван Петров",
                            "message_count": 15,
                            "last_active": "2 часа назад",
                            "status": "idle",
                        },
                    ],
                    "top_users": [
                        {
                            "user_display": "@maria_s",
                            "message_count": 156,
                            "percentage": 100.0,
                        },
                        {
                            "user_display": "Петр Иванов",
                            "message_count": 98,
                            "percentage": 62.8,
                        },
                    ],
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Ответ health check endpoint."""

    status: str = Field(default="ok", description="Статус сервера")
