"""Тесты для DateTimeTool."""

from src.datetime_tool import DateTimeTool


def test_datetime_tool_init():
    """Тест инициализации DateTimeTool."""
    # Act
    tool = DateTimeTool()

    # Assert
    assert tool is not None


def test_get_current_datetime_utc():
    """Тест получения текущей даты в UTC."""
    # Arrange
    tool = DateTimeTool()

    # Act
    result = tool.get_current_datetime("UTC", "full")

    # Assert
    assert result is not None
    assert "UTC" in result
    assert "-" in result  # Есть дата


def test_get_current_datetime_date_only():
    """Тест получения только даты."""
    # Arrange
    tool = DateTimeTool()

    # Act
    result = tool.get_current_datetime("UTC", "date")

    # Assert
    assert result is not None
    assert "UTC" not in result  # Нет часового пояса в date формате
    assert ":" not in result  # Нет времени


def test_get_current_datetime_time_only():
    """Тест получения только времени."""
    # Arrange
    tool = DateTimeTool()

    # Act
    result = tool.get_current_datetime("UTC", "time")

    # Assert
    assert result is not None
    assert ":" in result  # Есть время
    assert "UTC" in result


def test_get_current_datetime_moscow():
    """Тест получения времени в Москве."""
    # Arrange
    tool = DateTimeTool()

    # Act
    result = tool.get_current_datetime("Europe/Moscow", "full")

    # Assert
    assert result is not None
    assert "Europe/Moscow" in result


def test_get_current_datetime_invalid_timezone():
    """Тест с неправильным часовым поясом."""
    # Arrange
    tool = DateTimeTool()

    # Act - должен вернуть UTC при ошибке
    result = tool.get_current_datetime("Invalid/Timezone", "full")

    # Assert
    assert result is not None
    assert "UTC" in result  # Фолбэк на UTC
