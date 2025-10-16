"""Тесты для main модуля."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.main import main, setup_logging


def test_setup_logging_configures_levels():
    """Тест что setup_logging настраивает уровни для библиотек."""
    # Arrange - сбрасываем логгеры
    for logger_name in ["httpx", "httpcore", "openai", "aiogram"]:
        logging.getLogger(logger_name).setLevel(logging.NOTSET)

    # Act
    setup_logging("INFO")

    # Assert
    # Проверяем что библиотеки имеют правильные уровни
    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.getLogger("httpcore").level == logging.WARNING
    assert logging.getLogger("openai").level == logging.INFO
    assert logging.getLogger("aiogram").level == logging.INFO


def test_setup_logging_with_basicconfig():
    """Тест что setup_logging вызывает basicConfig."""
    with patch("logging.basicConfig") as mock_basic_config:
        # Act
        setup_logging("DEBUG")

        # Assert
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args.kwargs
        assert call_kwargs["level"] == logging.DEBUG


@pytest.mark.asyncio
async def test_main_creates_components(monkeypatch):
    """Тест что main создает все компоненты."""
    # Arrange
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")

    # Mock компоненты
    with patch("src.main.Config") as MockConfig:
        with patch("src.main.setup_logging"):
            with patch("src.main.ContextManager") as MockContextManager:
                with patch("src.main.LLMClient") as MockLLMClient:
                    with patch("src.main.MessageHandler") as MockMessageHandler:
                        with patch("src.main.TelegramBot") as MockTelegramBot:
                            # Настраиваем моки
                            mock_config = MagicMock()
                            mock_config.log_level = "INFO"
                            mock_config.openai_model = "gpt-5"
                            mock_config.max_context_messages = 10
                            MockConfig.return_value = mock_config

                            mock_bot = MagicMock()
                            mock_bot.start = AsyncMock()
                            MockTelegramBot.return_value = mock_bot

                            # Act
                            await main()

                            # Assert - проверяем что все компоненты созданы
                            MockConfig.assert_called_once()
                            mock_config.validate_config.assert_called_once()
                            MockContextManager.assert_called_once_with(mock_config)
                            MockLLMClient.assert_called_once_with(mock_config)
                            MockMessageHandler.assert_called_once()
                            MockTelegramBot.assert_called_once()
                            mock_bot.start.assert_called_once()


@pytest.mark.asyncio
async def test_main_calls_setup_logging(monkeypatch):
    """Тест что main вызывает setup_logging."""
    # Arrange
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")

    with patch("src.main.setup_logging") as mock_setup_logging:
        with patch("src.main.Config") as MockConfig:
            with patch("src.main.LLMClient"):
                with patch("src.main.TelegramBot") as MockTelegramBot:
                    # Настраиваем моки
                    mock_config = MagicMock()
                    mock_config.log_level = "DEBUG"
                    mock_config.openai_model = "gpt-5"
                    mock_config.max_context_messages = 10
                    MockConfig.return_value = mock_config

                    mock_bot = MagicMock()
                    mock_bot.start = AsyncMock()
                    MockTelegramBot.return_value = mock_bot

                    # Act
                    await main()

                    # Assert
                    mock_setup_logging.assert_called_once_with("DEBUG")


@pytest.mark.asyncio
async def test_main_validates_config(monkeypatch):
    """Тест что main валидирует конфигурацию."""
    # Arrange
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")

    with patch("src.main.Config") as MockConfig:
        with patch("src.main.setup_logging"):
            with patch("src.main.LLMClient"):
                with patch("src.main.TelegramBot") as MockTelegramBot:
                    # Настраиваем моки
                    mock_config = MagicMock()
                    mock_config.log_level = "INFO"
                    mock_config.openai_model = "gpt-5"
                    mock_config.max_context_messages = 10
                    MockConfig.return_value = mock_config

                    mock_bot = MagicMock()
                    mock_bot.start = AsyncMock()
                    MockTelegramBot.return_value = mock_bot

                    # Act
                    await main()

                    # Assert
                    mock_config.validate_config.assert_called_once()


@pytest.mark.asyncio
async def test_main_with_bot_start_error(monkeypatch):
    """Тест обработки ошибки при запуске бота."""
    # Arrange
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")

    with patch("src.main.Config") as MockConfig:
        with patch("src.main.setup_logging"):
            with patch("src.main.LLMClient"):
                with patch("src.main.TelegramBot") as MockTelegramBot:
                    # Настраиваем моки
                    mock_config = MagicMock()
                    mock_config.log_level = "INFO"
                    mock_config.openai_model = "gpt-5"
                    mock_config.max_context_messages = 10
                    MockConfig.return_value = mock_config

                    mock_bot = MagicMock()
                    mock_bot.start = AsyncMock(side_effect=Exception("Bot start failed"))
                    MockTelegramBot.return_value = mock_bot

                    # Act & Assert
                    with pytest.raises(Exception, match="Bot start failed"):
                        await main()
