"""StatCollector Protocol для сбора статистики."""

from typing import Literal, Protocol, runtime_checkable

from src.api.models import StatsResponse


@runtime_checkable
class StatCollector(Protocol):
    """
    Протокол для сборщиков статистики диалогов.

    Реализации:
    - MockStatCollector: генерация тестовых данных (FE-S1)
    - RealStatCollector: сбор реальных данных из БД (FE-S5)

    Example:
        >>> collector: StatCollector = MockStatCollector()
        >>> stats = collector.get_stats("day")
        >>> print(stats.general_stats.total_dialogs)
        245
    """

    def get_stats(self, period: Literal["day", "week", "month"]) -> StatsResponse:
        """
        Получить статистику диалогов за период.

        Args:
            period: Период анализа:
                - "day": последние 24 часа
                - "week": последние 7 дней
                - "month": последние 30 дней

        Returns:
            StatsResponse с агрегированными данными:
                - general_stats: общая статистика
                - activity_chart: данные для графика
                - recent_dialogs: последние диалоги
                - top_users: топ пользователей

        Raises:
            ValueError: Если period имеет невалидное значение
        """
        ...
