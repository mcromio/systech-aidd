"""FastAPI router для Stats API."""

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from src.api.mock import MockStatCollector
from src.api.models import HealthResponse, StatsResponse

logger = logging.getLogger(__name__)

# Создаем router для API endpoints
router = APIRouter()

# Инициализация Mock collector (глобальный singleton для консистентности данных)
_mock_collector = MockStatCollector(seed=42)


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Проверка работоспособности API сервера.

    Returns:
        HealthResponse с статусом "ok"

    Example:
        >>> GET /health
        {"status": "ok"}
    """
    logger.debug("Health check requested")
    return HealthResponse(status="ok")


@router.get(
    "/api/v1/stats",
    response_model=StatsResponse,
    tags=["Statistics"],
    summary="Получить статистику диалогов",
    description="""
    Получить агрегированную статистику диалогов за выбранный период.

    Возвращает:
    - Общую статистику (диалоги, пользователи, сообщения, средняя длина)
    - Данные для графика активности по времени
    - Список последних диалогов (макс 10)
    - Топ пользователей по активности (макс 5)

    **Примечание:** В текущей реализации используется Mock API с тестовыми данными.
    """,
)
def get_stats(
    period: Literal["day", "week", "month"] = Query(
        default="day",
        description="Период анализа: day (24 часа), week (7 дней), month (30 дней)",
        examples=["day", "week", "month"],
    ),
) -> StatsResponse:
    """
    Получить статистику диалогов за период.

    Args:
        period: Период анализа (day/week/month)

    Returns:
        StatsResponse с агрегированными данными

    Raises:
        HTTPException: 400 если period невалиден
        HTTPException: 500 если произошла внутренняя ошибка

    Example:
        >>> GET /api/v1/stats?period=day
        {
          "period": "day",
          "generated_at": "2025-10-17T11:05:00Z",
          "general_stats": {...},
          "activity_chart": [...],
          "recent_dialogs": [...],
          "top_users": [...]
        }
    """
    try:
        logger.info(f"Stats requested for period={period}")
        stats = _mock_collector.get_stats(period)
        logger.debug(f"Stats generated successfully: {stats.general_stats.total_dialogs} dialogs")
        return stats

    except ValueError as e:
        logger.error(f"Invalid period value: {period}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period value. Must be one of: day, week, month. Error: {str(e)}",
        ) from e
    except Exception as e:
        logger.exception(f"Error generating stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
