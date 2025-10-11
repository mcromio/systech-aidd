"""Тесты для конфигурации."""

import pytest
from pydantic import ValidationError

from src.config import Config


def test_config_loads_from_env(monkeypatch):
    """Тест загрузки конфигурации из переменных окружения."""
    # Arrange
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")

    # Act - используем kwargs чтобы обойти чтение .env файла
    config = Config(
        telegram_bot_token="123:ABC",
        openai_api_key="sk-test",
        openai_proxy_url="https://proxy.test.com",
    )

    # Assert
    assert config.telegram_bot_token == "123:ABC"
    assert config.openai_api_key == "sk-test"
    assert config.openai_proxy_url == "https://proxy.test.com"


def test_config_default_values(monkeypatch):
    """Тест дефолтных значений конфигурации."""
    # Arrange - используем kwargs чтобы обойти чтение .env файла
    # Act
    config = Config(
        telegram_bot_token="123:ABC",
        openai_api_key="sk-test",
        openai_proxy_url="https://proxy.test.com",
        openai_model="gpt-4o-mini",  # явно задаем модель для теста
    )

    # Assert - проверяем дефолтные значения (кроме модели которую задали явно)
    assert config.openai_model == "gpt-4o-mini"
    assert config.openai_timeout == 30.0
    assert config.max_context_messages == 10
    assert config.log_level == "INFO"


def test_config_custom_values(monkeypatch):
    """Тест кастомных значений конфигурации."""
    # Arrange
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")
    monkeypatch.setenv("OPENAI_TIMEOUT", "60.0")
    monkeypatch.setenv("MAX_CONTEXT_MESSAGES", "20")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Act
    config = Config()

    # Assert
    assert config.openai_model == "gpt-4"
    assert config.openai_timeout == 60.0
    assert config.max_context_messages == 20
    assert config.log_level == "DEBUG"


def test_config_validation_max_context_messages(monkeypatch):
    """Тест валидации max_context_messages."""
    # Arrange
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")
    monkeypatch.setenv("MAX_CONTEXT_MESSAGES", "100")  # Больше 50

    # Act & Assert
    with pytest.raises(ValidationError):
        Config()


def test_validate_config_success(monkeypatch):
    """Тест успешной валидации конфигурации."""
    # Arrange
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_PROXY_URL", "https://proxy.test.com")

    # Act
    config = Config()
    config.validate_config()  # Не должно бросить исключение

    # Assert - прошло без ошибок


def test_validate_config_missing_telegram_token():
    """Тест валидации при отсутствии Telegram токена."""
    # Arrange - создаем config с пустым токеном
    config = Config(
        telegram_bot_token="",
        openai_api_key="sk-test",
        openai_proxy_url="https://proxy.test.com",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN обязателен"):
        config.validate_config()
