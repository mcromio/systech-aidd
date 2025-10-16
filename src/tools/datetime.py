"""Инструмент для работы с датой и временем."""

import logging
from datetime import datetime
from typing import Any, Literal

import pytz

logger = logging.getLogger(__name__)


class DateTimeTool:
    """Инструмент для получения текущей даты и времени."""

    def __init__(self) -> None:
        """Инициализация DateTimeTool."""
        logger.info("DateTimeTool инициализирован")

    def get_schema(self) -> dict[str, Any]:
        """
        Возвращает JSON схему для OpenAI function calling.

        Returns:
            Схема функции в формате OpenAI
        """
        return {
            "type": "function",
            "function": {
                "name": "get_current_datetime",
                "description": "Получить текущую дату и время. Используй когда пользователь спрашивает 'какая сегодня дата', 'сколько времени', 'какой сейчас день недели' и т.п.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Часовой пояс (UTC, Europe/Moscow, America/New_York, Asia/Tokyo, etc.)",
                            "default": "UTC",
                        },
                        "format_type": {
                            "type": "string",
                            "enum": ["full", "date", "time"],
                            "description": "Формат: full (дата+время), date (только дата), time (только время)",
                            "default": "full",
                        },
                    },
                    "required": [],
                },
            },
        }

    async def execute(self, **kwargs: Any) -> str:
        """
        Выполняет инструмент с переданными аргументами.

        Args:
            **kwargs: timezone, format_type

        Returns:
            Текущая дата и время в указанном формате
        """
        timezone = kwargs.get("timezone", "UTC")
        format_type = kwargs.get("format_type", "full")
        return self.get_current_datetime(timezone, format_type)

    def get_current_datetime(
        self,
        timezone: str = "UTC",
        format_type: Literal["full", "date", "time"] = "full",
    ) -> str:
        """
        Получить текущую дату и время.

        Args:
            timezone: Часовой пояс (UTC, Europe/Moscow, America/New_York, etc.)
            format_type: Формат вывода - full (дата+время), date (только дата), time (только время)

        Returns:
            Текущая дата и время в указанном формате

        Examples:
            >>> tool = DateTimeTool()
            >>> tool.get_current_datetime("UTC", "full")
            "2025-10-10 19:50:00 UTC (четверг)"
            >>> tool.get_current_datetime("Europe/Moscow", "date")
            "2025-10-10 (четверг)"
        """
        try:
            # Получаем часовой пояс
            try:
                tz = pytz.timezone(timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                logger.warning(f"Неизвестный часовой пояс: {timezone}, используется UTC")
                tz = pytz.UTC

            # Получаем текущее время
            now = datetime.now(tz)

            # Форматируем в зависимости от типа
            weekday_ru = [
                "понедельник",
                "вторник",
                "среда",
                "четверг",
                "пятница",
                "суббота",
                "воскресенье",
            ][now.weekday()]

            if format_type == "date":
                result = f"{now.strftime('%Y-%m-%d')} ({weekday_ru})\n\n🕐 Источник: Текущая дата в часовом поясе {timezone}"
            elif format_type == "time":
                result = f"{now.strftime('%H:%M:%S')} {timezone}\n\n🕐 Источник: Текущее время в часовом поясе {timezone}"
            else:  # full
                result = f"{now.strftime('%Y-%m-%d %H:%M:%S')} {timezone} ({weekday_ru})\n\n🕐 Источник: Текущие дата и время в часовом поясе {timezone}"

            logger.debug(f"Получена дата/время: {result}")
            return result

        except Exception as e:
            logger.error(f"Ошибка при получении даты/времени: {e}", exc_info=True)
            return f"Ошибка при получении даты/времени: {e}"
