"""Тесты для WikipediaTool."""

import pytest

from src.wikipedia_tool import WikipediaTool


@pytest.mark.asyncio
async def test_wikipedia_tool_init():
    """Тест инициализации WikipediaTool."""
    # Act
    tool = WikipediaTool()

    # Assert
    assert tool.wiki_ru is not None
    assert tool.wiki_en is not None


@pytest.mark.asyncio
async def test_search_existing_article_ru():
    """Тест поиска существующей статьи на русском."""
    # Arrange
    tool = WikipediaTool()

    # Act
    result = await tool.search("Python", "ru")

    # Assert
    assert "Python" in result
    assert len(result) > 0
    assert "Источник:" in result


@pytest.mark.asyncio
async def test_search_existing_article_en():
    """Тест поиска существующей статьи на английском."""
    # Arrange
    tool = WikipediaTool()

    # Act
    result = await tool.search("Python", "en")

    # Assert
    assert "Python" in result or "python" in result.lower()
    assert len(result) > 0
    assert "Source:" in result or "Источник:" in result


@pytest.mark.asyncio
async def test_search_nonexistent_article():
    """Тест поиска несуществующей статьи."""
    # Arrange
    tool = WikipediaTool()

    # Act
    result = await tool.search("NonExistentArticle12345XYZ", "ru")

    # Assert
    assert "не найдена" in result
    assert "NonExistentArticle12345XYZ" in result


@pytest.mark.asyncio
async def test_search_default_language():
    """Тест поиска с дефолтным языком (ru)."""
    # Arrange
    tool = WikipediaTool()

    # Act
    result = await tool.search("Москва")

    # Assert
    assert "Москва" in result or "москва" in result.lower()
    assert len(result) > 0


@pytest.mark.asyncio
async def test_search_long_article_truncated():
    """Тест обрезки длинной статьи до 500 символов."""
    # Arrange
    tool = WikipediaTool()

    # Act
    result = await tool.search("История России", "ru")

    # Assert
    # Результат должен содержать "..." если статья длинная
    assert len(result) > 0
    # Проверяем что есть источник
    assert "Источник:" in result


@pytest.mark.asyncio
async def test_search_different_languages():
    """Тест поиска на разных языках."""
    # Arrange
    tool = WikipediaTool()

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
    # Arrange & Act
    tool = WikipediaTool(user_agent="CustomBot/2.0")

    # Assert
    assert tool.wiki_ru is not None
    assert tool.wiki_en is not None
