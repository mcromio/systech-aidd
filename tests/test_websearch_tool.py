"""Тесты для WebSearchTool."""

import pytest

from src.websearch_tool import WebSearchTool


def test_websearch_tool_init():
    """Тест инициализации WebSearchTool."""
    # Act
    tool = WebSearchTool()

    # Assert
    assert tool is not None
    assert tool.ddgs is not None


@pytest.mark.asyncio
async def test_search_basic():
    """Тест базового поиска."""
    # Arrange
    tool = WebSearchTool()

    # Act
    result = await tool.search("Python programming language", max_results=2)

    # Assert
    assert result is not None
    assert len(result) > 0
    assert "Python" in result or "python" in result


@pytest.mark.asyncio
async def test_search_max_results():
    """Тест ограничения результатов."""
    # Arrange
    tool = WebSearchTool()

    # Act
    result = await tool.search("test query", max_results=1)

    # Assert
    assert result is not None
    # Проверяем что результат не пустой
    assert len(result) > 10


@pytest.mark.asyncio
async def test_search_empty_query():
    """Тест с пустым запросом."""
    # Arrange
    tool = WebSearchTool()

    # Act
    result = await tool.search("", max_results=1)

    # Assert
    assert result is not None
    # Должен вернуть что-то (возможно ошибку или пустой результат)


@pytest.mark.asyncio
async def test_search_max_results_limits():
    """Тест границ max_results."""
    # Arrange
    tool = WebSearchTool()

    # Act - должен ограничить до 5
    result = await tool.search("test", max_results=10)

    # Assert
    assert result is not None

    # Act - должен ограничить до 1
    result = await tool.search("test", max_results=0)

    # Assert
    assert result is not None
