"""Тесты для MockStatCollector."""

import pytest

from src.api.collector import StatCollector
from src.api.mock import MockStatCollector
from src.api.models import StatsResponse


class TestMockStatCollector:
    """Тесты для Mock реализации StatCollector."""

    def test_collector_implements_protocol(self) -> None:
        """Тест: MockStatCollector реализует Protocol StatCollector."""
        collector = MockStatCollector()
        assert isinstance(collector, StatCollector)

    def test_get_stats_day_returns_valid_response(self) -> None:
        """Тест: get_stats для period=day возвращает валидный ответ."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        assert isinstance(stats, StatsResponse)
        assert stats.period == "day"
        assert stats.generated_at is not None

    def test_get_stats_week_returns_valid_response(self) -> None:
        """Тест: get_stats для period=week возвращает валидный ответ."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("week")

        assert isinstance(stats, StatsResponse)
        assert stats.period == "week"

    def test_get_stats_month_returns_valid_response(self) -> None:
        """Тест: get_stats для period=month возвращает валидный ответ."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("month")

        assert isinstance(stats, StatsResponse)
        assert stats.period == "month"

    def test_get_stats_invalid_period_raises_error(self) -> None:
        """Тест: невалидный period вызывает ValueError."""
        collector = MockStatCollector()

        with pytest.raises(ValueError, match="Invalid period"):
            collector.get_stats("invalid")  # type: ignore

    def test_general_stats_has_positive_values(self) -> None:
        """Тест: общая статистика содержит положительные значения."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        assert stats.general_stats.total_dialogs > 0
        assert stats.general_stats.active_users > 0
        assert stats.general_stats.total_messages > 0
        assert stats.general_stats.avg_dialog_length > 0

    def test_general_stats_change_is_percentage(self) -> None:
        """Тест: проценты изменений в разумных пределах."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        # Проценты обычно в диапазоне ±50%
        assert -50 <= stats.general_stats.total_dialogs_change <= 50
        assert -50 <= stats.general_stats.active_users_change <= 50
        assert -50 <= stats.general_stats.total_messages_change <= 50

    def test_activity_chart_day_has_24_points(self) -> None:
        """Тест: график для day содержит 24 точки (по часам)."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        assert len(stats.activity_chart) == 24

        # Проверка формата времени (00:00, 01:00, ..., 23:00)
        assert stats.activity_chart[0].time == "00:00"
        assert stats.activity_chart[12].time == "12:00"
        assert stats.activity_chart[23].time == "23:00"

    def test_activity_chart_week_has_7_points(self) -> None:
        """Тест: график для week содержит 7 точек (по дням)."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("week")

        assert len(stats.activity_chart) == 7

        # Проверка формата дней недели
        days = [point.time for point in stats.activity_chart]
        assert "Пн" in days
        assert "Вс" in days

    def test_activity_chart_month_has_30_points(self) -> None:
        """Тест: график для month содержит 30 точек (по дням)."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("month")

        assert len(stats.activity_chart) == 30

        # Проверка формата (1, 2, ..., 30)
        assert stats.activity_chart[0].time == "1"
        assert stats.activity_chart[29].time == "30"

    def test_activity_chart_messages_are_positive(self) -> None:
        """Тест: количество сообщений в графике положительное."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        for point in stats.activity_chart:
            assert point.messages >= 0

    def test_recent_dialogs_has_max_10_items(self) -> None:
        """Тест: список последних диалогов содержит максимум 10 элементов."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        assert len(stats.recent_dialogs) <= 10

    def test_recent_dialogs_have_valid_status(self) -> None:
        """Тест: статусы диалогов валидны (active/idle/inactive)."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        valid_statuses = ["active", "idle", "inactive"]
        for dialog in stats.recent_dialogs:
            assert dialog.status in valid_statuses

    def test_recent_dialogs_have_positive_message_count(self) -> None:
        """Тест: количество сообщений в диалогах положительное."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        for dialog in stats.recent_dialogs:
            assert dialog.message_count > 0

    def test_top_users_has_max_5_items(self) -> None:
        """Тест: топ пользователей содержит максимум 5 элементов."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        assert len(stats.top_users) <= 5

    def test_top_users_first_has_100_percent(self) -> None:
        """Тест: первый пользователь в топе имеет 100% активности."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        if stats.top_users:
            assert stats.top_users[0].percentage == 100.0

    def test_top_users_percentage_in_range(self) -> None:
        """Тест: процент активности пользователей в диапазоне 0-100."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        for user in stats.top_users:
            assert 0 <= user.percentage <= 100

    def test_top_users_sorted_by_message_count(self) -> None:
        """Тест: пользователи в топе отсортированы по убыванию сообщений."""
        collector = MockStatCollector(seed=42)
        stats = collector.get_stats("day")

        if len(stats.top_users) > 1:
            for i in range(len(stats.top_users) - 1):
                assert stats.top_users[i].message_count >= stats.top_users[i + 1].message_count

    def test_seed_produces_reproducible_results(self) -> None:
        """Тест: один и тот же seed дает воспроизводимые результаты."""
        collector1 = MockStatCollector(seed=42)
        collector2 = MockStatCollector(seed=42)

        stats1 = collector1.get_stats("day")
        stats2 = collector2.get_stats("day")

        # Проверяем что данные идентичны
        assert stats1.general_stats.total_dialogs == stats2.general_stats.total_dialogs
        assert stats1.general_stats.active_users == stats2.general_stats.active_users
        assert len(stats1.activity_chart) == len(stats2.activity_chart)

    def test_different_periods_produce_different_data(self) -> None:
        """Тест: разные периоды дают разные данные."""
        collector = MockStatCollector(seed=42)

        stats_day = collector.get_stats("day")
        stats_week = collector.get_stats("week")
        stats_month = collector.get_stats("month")

        # Проверяем что данные отличаются
        assert stats_day.general_stats.total_dialogs != stats_week.general_stats.total_dialogs
        assert stats_week.general_stats.total_dialogs != stats_month.general_stats.total_dialogs
        assert len(stats_day.activity_chart) != len(stats_week.activity_chart)

    def test_month_has_more_data_than_day(self) -> None:
        """Тест: данные за месяц больше чем за день."""
        collector = MockStatCollector(seed=42)

        stats_day = collector.get_stats("day")
        stats_month = collector.get_stats("month")

        # За месяц должно быть больше диалогов и сообщений
        assert stats_month.general_stats.total_dialogs > stats_day.general_stats.total_dialogs
        assert stats_month.general_stats.total_messages > stats_day.general_stats.total_messages
