"""Тесты для MessageHandler."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Message as TelegramMessage
from aiogram.types import User

from src.config import Config
from src.context_manager import ContextManager
from src.handlers import MessageHandler
from src.llm_client import LLMClient


@pytest.fixture
def config(monkeypatch):
    """Фикстура конфигурации."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")
    return Config()


@pytest.fixture
def context_manager(config):
    """Фикстура ContextManager."""
    return ContextManager(config)


@pytest.fixture
def llm_client(config):
    """Фикстура LLMClient (mock)."""
    return MagicMock(spec=LLMClient)


@pytest.fixture
def message_handler(config, context_manager, llm_client):
    """Фикстура MessageHandler."""
    return MessageHandler(config, context_manager, llm_client)


@pytest.fixture
def mock_telegram_message():
    """Фикстура Telegram сообщения."""
    message = MagicMock(spec=TelegramMessage)
    message.from_user = User(id=123, is_bot=False, first_name="Test")
    message.answer = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_handle_start(message_handler, mock_telegram_message):
    """Тест команды /start."""
    # Act
    await message_handler.handle_start(mock_telegram_message)

    # Assert
    mock_telegram_message.answer.assert_called_once()
    call_args = mock_telegram_message.answer.call_args[0][0]
    assert "Привет" in call_args
    assert "/help" in call_args


@pytest.mark.asyncio
async def test_handle_help(message_handler, mock_telegram_message):
    """Тест команды /help."""
    # Act
    await message_handler.handle_help(mock_telegram_message)

    # Assert
    mock_telegram_message.answer.assert_called_once()
    call_args = mock_telegram_message.answer.call_args[0][0]
    assert "Справка" in call_args
    assert "/reset" in call_args


@pytest.mark.asyncio
async def test_handle_reset(message_handler, mock_telegram_message, context_manager):
    """Тест команды /reset."""
    # Arrange
    user_id = mock_telegram_message.from_user.id
    context_manager.add_message(user_id, "user", "Test")

    # Act
    await message_handler.handle_reset(mock_telegram_message)

    # Assert
    assert len(context_manager.get_history(user_id)) == 0
    mock_telegram_message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_message_success(
    message_handler, mock_telegram_message, llm_client, context_manager
):
    """Тест успешной обработки сообщения."""
    # Arrange
    user_id = mock_telegram_message.from_user.id
    mock_telegram_message.text = "Hello!"
    llm_client.get_response = AsyncMock(return_value="Hi there!")

    # Act
    await message_handler.handle_message(mock_telegram_message)

    # Assert
    history = context_manager.get_history(user_id)
    assert len(history) == 2  # user + assistant
    assert history[0].content == "Hello!"
    assert history[1].content == "Hi there!"
    mock_telegram_message.answer.assert_called_once_with("Hi there!")


@pytest.mark.asyncio
async def test_handle_message_llm_returns_none(message_handler, mock_telegram_message, llm_client):
    """Тест обработки сообщения когда LLM возвращает None."""
    # Arrange
    mock_telegram_message.text = "Hello!"
    llm_client.get_response = AsyncMock(return_value=None)

    # Act
    await message_handler.handle_message(mock_telegram_message)

    # Assert
    mock_telegram_message.answer.assert_called_once()
    call_args = mock_telegram_message.answer.call_args[0][0]
    assert "ошибка" in call_args.lower()


@pytest.mark.asyncio
async def test_handle_message_exception(message_handler, mock_telegram_message, llm_client):
    """Тест обработки исключения при обработке сообщения."""
    # Arrange
    mock_telegram_message.text = "Hello!"
    llm_client.get_response = AsyncMock(side_effect=Exception("Test error"))

    # Act
    await message_handler.handle_message(mock_telegram_message)

    # Assert
    mock_telegram_message.answer.assert_called_once()
    call_args = mock_telegram_message.answer.call_args[0][0]
    assert "ошибка" in call_args.lower()
