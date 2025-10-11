"""Тесты для TelegramBot."""

from unittest.mock import AsyncMock, patch

import pytest

from src.bot import TelegramBot
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
def message_handler(config):
    """Фикстура MessageHandler."""
    context_manager = ContextManager(config)
    llm_client = LLMClient(config, tools=[])
    return MessageHandler(config, context_manager, llm_client)


@pytest.mark.asyncio
async def test_telegram_bot_init(config, message_handler):
    """Тест инициализации TelegramBot."""
    # Act
    bot = TelegramBot(config, message_handler)

    # Assert
    assert bot.config == config
    assert bot.message_handler == message_handler
    assert bot.bot is not None
    assert bot.dp is not None


@pytest.mark.asyncio
async def test_register_handlers(config, message_handler):
    """Тест регистрации handlers."""
    # Arrange
    bot = TelegramBot(config, message_handler)

    # Spy на register методы
    with patch.object(bot.dp.message, "register") as mock_register:
        # Act
        bot.register_handlers()

        # Assert
        # Проверяем что register вызывался 4 раза
        # (/start, /help, /reset, handle_message)
        assert mock_register.call_count == 4


@pytest.mark.asyncio
async def test_start_success(config, message_handler):
    """Тест успешного запуска бота."""
    # Arrange
    bot = TelegramBot(config, message_handler)

    # Mock start_polling
    with patch.object(bot.dp, "start_polling", new_callable=AsyncMock) as mock_polling:
        with patch.object(bot.bot.session, "close", new_callable=AsyncMock) as mock_close:
            # Act
            await bot.start()

            # Assert
            mock_polling.assert_called_once_with(bot.bot)
            mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_start_with_error(config, message_handler):
    """Тест обработки ошибки при запуске бота."""
    # Arrange
    bot = TelegramBot(config, message_handler)

    # Mock start_polling с ошибкой
    with patch.object(
        bot.dp, "start_polling", new_callable=AsyncMock, side_effect=Exception("Polling error")
    ):
        with patch.object(bot.bot.session, "close", new_callable=AsyncMock) as mock_close:
            # Act & Assert
            with pytest.raises(Exception, match="Polling error"):
                await bot.start()

            # Session должна закрыться даже при ошибке
            mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_register_handlers_called_in_start(config, message_handler):
    """Тест что register_handlers вызывается в start()."""
    # Arrange
    bot = TelegramBot(config, message_handler)

    # Mock методы
    with patch.object(bot, "register_handlers") as mock_register:
        with patch.object(bot.dp, "start_polling", new_callable=AsyncMock):
            with patch.object(bot.bot.session, "close", new_callable=AsyncMock):
                # Act
                await bot.start()

                # Assert
                mock_register.assert_called_once()
