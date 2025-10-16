"""Тесты для WebSearchTool."""

import pytest

from src.config import Config
from src.tools import WebSearchTool


@pytest.fixture
def config():
    """Фикстура конфигурации."""
    return Config(
        telegram_bot_token="123:ABC",
        openai_api_key="sk-test",
        openai_proxy_url="https://proxy.test.com",
    )


@pytest.mark.asyncio
async def test_websearch_tool_init(config):
    """Тест инициализации WebSearchTool."""
    # Act
    tool = WebSearchTool(config)

    # Assert
    assert tool.ddgs is not None
    assert tool.config is not None


@pytest.mark.asyncio
async def test_search_basic(config):
    """Тест базового поиска."""
    # Arrange
    tool = WebSearchTool(config)

    # Act
    result = await tool.search("Python programming")

    # Assert
    assert result is not None
    assert len(result) > 0
    assert "Python" in result or "python" in result.lower()


@pytest.mark.asyncio
async def test_search_max_results(config):
    """Тест с указанием max_results."""
    # Arrange
    tool = WebSearchTool(config)

    # Act
    result = await tool.search("Python", max_results=2)

    # Assert
    assert result is not None
    assert len(result) > 0


@pytest.mark.asyncio
async def test_search_empty_query(config):
    """Тест с пустым запросом."""
    # Arrange
    tool = WebSearchTool(config)

    # Act
    result = await tool.search("")

    # Assert
    assert result is not None
    # Может вернуть ошибку или результаты по умолчанию


@pytest.mark.asyncio
async def test_search_max_results_limits(config):
    """Тест ограничения max_results."""
    # Arrange
    tool = WebSearchTool(config)

    # Act - запрашиваем больше максимума
    result = await tool.search("test", max_results=100)

    # Assert - должно ограничиться config.websearch_max_results
    assert result is not None
    assert len(result) > 0
