"""Тесты для WikipediaTool."""

import pytest

from src.config import Config
from src.wikipedia_tool import WikipediaTool


@pytest.fixture
def config():
    """Фикстура конфигурации."""
    return Config(
        telegram_bot_token="123:ABC",
        openai_api_key="sk-test",
        openai_proxy_url="https://proxy.test.com",
    )


@pytest.mark.asyncio
async def test_wikipedia_tool_init(config):
    """Тест инициализации WikipediaTool."""
    # Act
    tool = WikipediaTool(config)

    # Assert
    assert tool.wiki_ru is not None
    assert tool.wiki_en is not None


@pytest.mark.asyncio
async def test_search_existing_article_ru(config):
    """Тест поиска существующей статьи на русском."""
    # Arrange
    tool = WikipediaTool(config)

    # Act
    result = await tool.search("Python", "ru")

    # Assert
    assert "Python" in result
    assert len(result) > 0
    assert "Источник:" in result


@pytest.mark.asyncio
async def test_search_existing_article_en(config):
    """Тест поиска существующей статьи на английском."""
    # Arrange
    tool = WikipediaTool(config)

    # Act
    result = await tool.search("Python", "en")

    # Assert
    assert "Python" in result or "python" in result.lower()
    assert len(result) > 0
    assert "Source:" in result or "Источник:" in result


@pytest.mark.asyncio
async def test_search_nonexistent_article(config):
    """Тест поиска несуществующей статьи."""
    # Arrange
    tool = WikipediaTool(config)

    # Act
    result = await tool.search("NonExistentArticle12345XYZ", "ru")

    # Assert
    assert "не найдена" in result.lower()


@pytest.mark.asyncio
async def test_search_default_language(config):
    """Тест дефолтного языка (русский)."""
    # Arrange
    tool = WikipediaTool(config)

    # Act - не указываем язык, должен использоваться дефолтный (ru)
    result = await tool.search("Москва")

    # Assert
    assert len(result) > 0
    assert "Москва" in result


@pytest.mark.asyncio
async def test_search_long_article_truncated(config):
    """Тест обрезки длинной статьи."""
    # Arrange
    tool = WikipediaTool(config)

    # Act - ищем большую статью
    result = await tool.search("Российская Федерация", "ru")

    # Assert
    assert len(result) > 0
    # Проверяем что результат обрезан (есть "...")
    # Summary + "\n\nИсточник: ..." должен быть не больше ~600 символов
    assert "..." in result or len(result) < 1000


@pytest.mark.asyncio
async def test_search_different_languages(config):
    """Тест поиска на разных языках."""
    # Arrange
    tool = WikipediaTool(config)

    # Act
    result_ru = await tool.search("Компьютер", "ru")
    result_en = await tool.search("Computer", "en")

    # Assert
    assert len(result_ru) > 0
    assert len(result_en) > 0
    assert result_ru != result_en


@pytest.mark.asyncio
async def test_custom_user_agent():
    """Тест кастомного user agent."""
    # Arrange - создаем config с кастомным user agent
    config = Config(
        telegram_bot_token="123:ABC",
        openai_api_key="sk-test",
        openai_proxy_url="https://proxy.test.com",
        wikipedia_user_agent="CustomBot/2.0",
    )

    # Act
    tool = WikipediaTool(config)

    # Assert
    assert tool.wiki_ru is not None
    assert tool.wiki_en is not None
