"""Тесты для LLMClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import Config
from src.context_manager import Message
from src.llm_client import LLMClient


@pytest.fixture
def config(monkeypatch):
    """Фикстура конфигурации."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.test.com")
    return Config()


@pytest.mark.asyncio
async def test_llm_client_init(config):
    """Тест инициализации LLMClient."""
    # Act
    client = LLMClient(config, None)

    # Assert
    assert client.config == config
    assert client.wikipedia_tool is None
    assert client.client is not None


@pytest.mark.asyncio
async def test_get_response_success(config):
    """Тест успешного получения ответа от LLM."""
    # Arrange
    client = LLMClient(config, None)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello! How can I help you?"

    # Mock OpenAI API
    with patch.object(
        client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        # Act
        messages = [Message(role="user", content="Hello")]
        response = await client.get_response(messages)

    # Assert
    assert response == "Hello! How can I help you?"


@pytest.mark.asyncio
async def test_get_response_with_history(config):
    """Тест получения ответа с историей диалога."""
    # Arrange
    client = LLMClient(config, None)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "I remember our conversation!"

    # Mock OpenAI API
    with patch.object(
        client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_create:
        # Act
        messages = [
            Message(role="user", content="My name is Alice"),
            Message(role="assistant", content="Nice to meet you, Alice!"),
            Message(role="user", content="What is my name?"),
        ]
        response = await client.get_response(messages)

        # Assert
        assert response == "I remember our conversation!"
        assert mock_create.called
        call_args = mock_create.call_args
        # Проверяем что в запросе есть system prompt + 3 сообщения
        assert len(call_args.kwargs["messages"]) == 4


@pytest.mark.asyncio
async def test_get_response_empty_messages(config):
    """Тест с пустым списком сообщений."""
    # Arrange
    client = LLMClient(config, None)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "How can I help you?"

    # Mock OpenAI API
    with patch.object(
        client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        # Act
        response = await client.get_response([])

    # Assert
    assert response == "How can I help you?"


@pytest.mark.asyncio
async def test_get_response_api_error(config):
    """Тест обработки ошибки API."""
    # Arrange
    client = LLMClient(config, None)

    # Mock OpenAI API с ошибкой
    with patch.object(
        client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        side_effect=Exception("API Error"),
    ):
        # Act
        messages = [Message(role="user", content="Hello")]
        response = await client.get_response(messages)

    # Assert
    assert response is None


@pytest.mark.asyncio
async def test_get_response_includes_system_prompt(config):
    """Тест что запрос включает системный промпт."""
    # Arrange
    client = LLMClient(config, None)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"

    # Mock OpenAI API
    with patch.object(
        client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_create:
        # Act
        messages = [Message(role="user", content="Test")]
        await client.get_response(messages)

        # Assert
        call_args = mock_create.call_args
        request_messages = call_args.kwargs["messages"]
        # Первое сообщение должно быть system prompt
        assert request_messages[0]["role"] == "system"
        assert request_messages[0]["content"] == config.system_prompt


@pytest.mark.asyncio
async def test_get_response_uses_correct_model(config):
    """Тест что используется правильная модель."""
    # Arrange
    client = LLMClient(config, None)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"

    # Mock OpenAI API
    with patch.object(
        client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_create:
        # Act
        messages = [Message(role="user", content="Test")]
        await client.get_response(messages)

        # Assert
        call_args = mock_create.call_args
        assert call_args.kwargs["model"] == config.openai_model
        assert call_args.kwargs["temperature"] == 0.7
        assert call_args.kwargs["max_tokens"] == 2000
