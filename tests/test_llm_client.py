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
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")
    return Config()


@pytest.mark.asyncio
async def test_llm_client_init(config):
    """Тест инициализации LLMClient."""
    # Act
    client = LLMClient(config)

    # Assert
    assert client.config == config
    assert client.client is not None
    assert len(client.tools) == 3  # WikipediaTool, DateTimeTool, WebSearchTool


@pytest.mark.asyncio
async def test_get_response_success(config):
    """Тест успешного получения ответа от LLM."""
    # Arrange
    client = LLMClient(config, tools=[])

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello! How can I help you?"
    mock_response.choices[0].message.tool_calls = None

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
    mock_response.choices[0].message.tool_calls = None

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
    mock_response.choices[0].message.tool_calls = None

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
    mock_response.choices[0].message.tool_calls = None

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
    client = LLMClient(config, tools=[])

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_response.choices[0].message.tool_calls = None

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
        # temperature удален для gpt-5
        # max_completion_tokens = config.llm_max_tokens_no_tools когда tools=[]
        assert call_args.kwargs["max_completion_tokens"] == config.llm_max_tokens_no_tools


@pytest.mark.asyncio
async def test_get_tools_schema_with_wikipedia(config):
    """Тест генерации схемы tools с дефолтными инструментами."""
    client = LLMClient(config)  # использует _get_default_tools()

    tools = client._get_tools_schema()

    # 3 tools по умолчанию: wikipedia + datetime + websearch
    assert len(tools) == 3
    tool_names = [t["function"]["name"] for t in tools]
    assert "search_wikipedia" in tool_names
    assert "get_current_datetime" in tool_names
    assert "web_search" in tool_names

    # Проверяем структуру wikipedia tool
    wiki_tool_schema = next(t for t in tools if t["function"]["name"] == "search_wikipedia")
    assert wiki_tool_schema["type"] == "function"
    assert "query" in wiki_tool_schema["function"]["parameters"]["properties"]


@pytest.mark.asyncio
async def test_get_tools_schema_without_tools(config):
    """Тест генерации схемы tools без инструментов."""
    client = LLMClient(config, tools=[])

    tools = client._get_tools_schema()

    # Нет инструментов
    assert len(tools) == 0


@pytest.mark.asyncio
async def test_execute_tool_wikipedia(config):
    """Тест выполнения Wikipedia tool."""
    from src.tools import WikipediaTool

    wiki_tool = WikipediaTool(config)
    client = LLMClient(config, tools=[wiki_tool])

    result = await client._execute_tool("search_wikipedia", {"query": "Python", "language": "en"})

    assert result is not None
    assert len(result) > 0


@pytest.mark.asyncio
async def test_execute_tool_unknown(config):
    """Тест вызова несуществующего tool."""
    client = LLMClient(config, tools=[])

    result = await client._execute_tool("unknown_tool", {})

    assert "Ошибка" in result or "не найден" in result


@pytest.mark.asyncio
async def test_get_response_with_tool_calls(config):
    """Тест обработки tool calls."""
    from src.tools import WikipediaTool

    wiki_tool = WikipediaTool(config)
    client = LLMClient(config, tools=[wiki_tool])

    # Mock первого ответа с tool call
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_123"
    mock_tool_call.function.name = "search_wikipedia"
    mock_tool_call.function.arguments = '{"query": "Python", "language": "en"}'

    mock_message_with_tools = MagicMock()
    mock_message_with_tools.tool_calls = [mock_tool_call]
    mock_message_with_tools.content = None
    mock_message_with_tools.model_dump.return_value = {
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "call_123", "function": {"name": "search_wikipedia"}}],
    }

    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock()]
    mock_response_1.choices[0].message = mock_message_with_tools

    # Mock второго ответа (финальный)
    mock_message_final = MagicMock()
    mock_message_final.tool_calls = None
    mock_message_final.content = "Python is a programming language..."

    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock()]
    mock_response_2.choices[0].message = mock_message_final

    # Mock OpenAI API с двумя вызовами
    with patch.object(
        client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        side_effect=[mock_response_1, mock_response_2],
    ):
        messages = [Message(role="user", content="Tell me about Python")]
        response = await client.get_response(messages)

    assert response == "Python is a programming language..."
