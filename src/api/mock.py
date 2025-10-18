"""Mock реализация StatCollector для тестовых данных."""

import logging
import random
from datetime import UTC, datetime
from typing import Literal

from src.api.collector import StatCollector
from src.api.models import (
    ActivityDataPoint,
    DialogInfo,
    GeneralStats,
    StatsResponse,
    UserActivity,
)

logger = logging.getLogger(__name__)


class MockStatCollector(StatCollector):
    """
    Mock реализация сборщика статистики.

    Генерирует реалистичные тестовые данные для разработки frontend
    без зависимости от реальной БД.

    Attributes:
        seed: Seed для генератора случайных чисел (для воспроизводимости)

    Example:
        >>> collector = MockStatCollector(seed=42)
        >>> stats = collector.get_stats("day")
        >>> print(stats.general_stats.total_dialogs)
        245
    """

    def __init__(self, seed: int = 42) -> None:
        """
        Инициализация Mock collector.

        Args:
            seed: Seed для random генератора (по умолчанию 42)
        """
        self.seed = seed
        random.seed(seed)
        logger.info(f"MockStatCollector initialized with seed={seed}")

    def get_stats(self, period: Literal["day", "week", "month"]) -> StatsResponse:
        """
        Получить mock статистику за период.

        Args:
            period: Период анализа (day/week/month)

        Returns:
            StatsResponse с сгенерированными данными

        Raises:
            ValueError: Если period невалиден
        """
        if period not in ["day", "week", "month"]:
            raise ValueError(f"Invalid period: {period}. Must be one of: day, week, month")

        logger.info(f"Generating mock stats for period={period}")

        # Сброс seed для каждого запроса (воспроизводимость)
        random.seed(self.seed + hash(period))

        return StatsResponse(
            period=period,
            generated_at=datetime.now(UTC),
            general_stats=self._generate_general_stats(period),
            activity_chart=self._generate_activity_chart(period),
            recent_dialogs=self._generate_recent_dialogs(period),
            top_users=self._generate_top_users(period),
        )

    def _generate_general_stats(self, period: str) -> GeneralStats:
        """
        Генерация общей статистики.

        Значения зависят от периода:
        - day: меньше всего
        - week: средние значения
        - month: больше всего
        """
        # Базовые множители для разных периодов
        multiplier = {"day": 1.0, "week": 3.5, "month": 12.0}[period]

        base_dialogs = int(245 * multiplier)
        base_users = int(89 * multiplier)
        base_messages = int(1543 * multiplier)

        # Добавляем некоторую случайность (±10%)
        total_dialogs = int(base_dialogs * random.uniform(0.9, 1.1))
        active_users = int(base_users * random.uniform(0.9, 1.1))
        total_messages = int(base_messages * random.uniform(0.9, 1.1))

        # Средняя длина диалога (реалистичная)
        avg_dialog_length = round(total_messages / max(total_dialogs, 1), 1)

        # Процент изменений (±5-20%)
        total_dialogs_change = round(random.uniform(-15.0, 20.0), 1)
        active_users_change = round(random.uniform(-10.0, 15.0), 1)
        total_messages_change = round(random.uniform(-12.0, 25.0), 1)
        avg_dialog_length_change = round(random.uniform(-8.0, 10.0), 1)

        return GeneralStats(
            total_dialogs=total_dialogs,
            total_dialogs_change=total_dialogs_change,
            active_users=active_users,
            active_users_change=active_users_change,
            total_messages=total_messages,
            total_messages_change=total_messages_change,
            avg_dialog_length=avg_dialog_length,
            avg_dialog_length_change=avg_dialog_length_change,
        )

    def _generate_activity_chart(self, period: str) -> list[ActivityDataPoint]:
        """
        Генерация данных для графика активности.

        - day: 24 точки (почасовая активность)
        - week: 7 точек (по дням недели)
        - month: 30 точек (по дням месяца)
        """
        if period == "day":
            return self._generate_hourly_activity()
        elif period == "week":
            return self._generate_weekly_activity()
        else:  # month
            return self._generate_monthly_activity()

    def _generate_hourly_activity(self) -> list[ActivityDataPoint]:
        """Генерация почасовой активности (24 точки)."""
        data_points = []

        # Паттерн активности по часам (реалистичный)
        # Низкая активность ночью (00:00-06:00)
        # Рост утром (07:00-09:00)
        # Стабильная в течение дня (10:00-18:00)
        # Пик вечером (19:00-22:00)
        # Снижение ночью (23:00)
        activity_pattern = [
            0.1,  # 00:00
            0.05,  # 01:00
            0.05,  # 02:00
            0.05,  # 03:00
            0.05,  # 04:00
            0.1,  # 05:00
            0.2,  # 06:00
            0.5,  # 07:00
            0.8,  # 08:00
            1.0,  # 09:00
            1.0,  # 10:00
            0.9,  # 11:00
            0.8,  # 12:00
            0.7,  # 13:00
            0.9,  # 14:00
            1.0,  # 15:00
            0.95,  # 16:00
            0.9,  # 17:00
            0.85,  # 18:00
            1.2,  # 19:00
            1.3,  # 20:00
            1.2,  # 21:00
            0.8,  # 22:00
            0.4,  # 23:00
        ]

        base_messages = 100
        for hour, multiplier in enumerate(activity_pattern):
            messages = int(base_messages * multiplier * random.uniform(0.8, 1.2))
            data_points.append(ActivityDataPoint(time=f"{hour:02d}:00", messages=messages))

        return data_points

    def _generate_weekly_activity(self) -> list[ActivityDataPoint]:
        """Генерация активности по дням недели (7 точек)."""
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        # Реалистичный паттерн: будни активнее выходных
        weekday_multiplier = [1.0, 1.05, 1.1, 1.0, 0.95, 0.6, 0.5]

        base_messages = 700
        data_points = []

        for day, multiplier in zip(days, weekday_multiplier, strict=True):
            messages = int(base_messages * multiplier * random.uniform(0.9, 1.1))
            data_points.append(ActivityDataPoint(time=day, messages=messages))

        return data_points

    def _generate_monthly_activity(self) -> list[ActivityDataPoint]:
        """Генерация активности по дням месяца (30 точек)."""
        data_points = []
        base_messages = 200

        for day in range(1, 31):
            # Добавляем тренд: в начале месяца чуть больше активности
            trend_multiplier = 1.2 - (day / 30) * 0.4
            messages = int(base_messages * trend_multiplier * random.uniform(0.7, 1.3))
            data_points.append(ActivityDataPoint(time=str(day), messages=messages))

        return data_points

    def _generate_recent_dialogs(self, period: str) -> list[DialogInfo]:
        """
        Генерация списка последних диалогов (макс 10).

        Реалистичные имена пользователей (русские и латинские).
        """
        usernames = [
            "@john_doe",
            "Иван Петров",
            "@maria_s",
            "Анна Сидорова",
            "@alex_k",
            "Петр Иванов",
            "@elena_m",
            "Сергей Смирнов",
            "@dmitry_p",
            "Ольга Козлова",
        ]

        dialogs = []

        for i, username in enumerate(usernames):
            # Генерация времени последней активности
            minutes_ago = random.randint(1, 60) if i < 2 else random.randint(60, 1440)

            # Форматирование относительного времени
            if minutes_ago < 60:
                last_active = f"{minutes_ago} минут назад"
                status = "active" if minutes_ago < 5 else "idle"
            elif minutes_ago < 1440:
                hours = minutes_ago // 60
                last_active = (
                    f"{hours} {'час' if hours == 1 else 'часа' if hours < 5 else 'часов'} назад"
                )
                status = "idle"
            else:
                days = minutes_ago // 1440
                last_active = (
                    f"{days} {'день' if days == 1 else 'дня' if days < 5 else 'дней'} назад"
                )
                status = "inactive"

            # Количество сообщений в диалоге
            message_count = random.randint(3, 25)

            dialogs.append(
                DialogInfo(
                    user_display=username,
                    message_count=message_count,
                    last_active=last_active,
                    status=status,  # type: ignore
                )
            )

        return dialogs

    def _generate_top_users(self, period: str) -> list[UserActivity]:
        """
        Генерация топ-5 пользователей по активности.

        Процент активности рассчитывается относительно самого активного.
        """
        usernames = [
            "@maria_s",
            "Петр Иванов",
            "@alex_k",
            "Анна Сидорова",
            "@john_doe",
        ]

        # Генерация количества сообщений (убывающий порядок)
        base_messages = random.randint(120, 200)
        message_counts = []

        for i in range(len(usernames)):
            # Убывающее количество сообщений
            multiplier = 1.0 - (i * 0.2)
            message_count = int(base_messages * multiplier * random.uniform(0.9, 1.1))
            message_counts.append(message_count)

        # Находим максимум для расчета процентов
        max_messages = max(message_counts) if message_counts else 1

        # Создаем UserActivity с корректными процентами
        top_users = []
        for username, message_count in zip(usernames, message_counts, strict=True):
            percentage = round((message_count / max_messages) * 100, 1)
            percentage = min(percentage, 100.0)  # Гарантируем что не превышаем 100%

            top_users.append(
                UserActivity(
                    user_display=username, message_count=message_count, percentage=percentage
                )
            )

        # Первый пользователь всегда должен иметь 100%
        if top_users:
            top_users[0].percentage = 100.0

        return top_users
