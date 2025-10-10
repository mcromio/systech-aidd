"""Тесты для ContextManager."""

import pytest

from src.config import Config
from src.context_manager import ContextManager, Message, UserContext


def test_message_creation():
    """Тест создания модели Message."""
    # Arrange & Act
    message = Message(role="user", content="Hello")

    # Assert
    assert message.role == "user"
    assert message.content == "Hello"


def test_user_context_add_message():
    """Тест добавления сообщения в UserContext."""
    # Arrange
    context = UserContext(user_id=123)

    # Act
    context.add_message("user", "Hello")

    # Assert
    assert len(context.messages) == 1
    assert context.messages[0].role == "user"
    assert context.messages[0].content == "Hello"


def test_user_context_get_messages():
    """Тест получения сообщений из UserContext."""
    # Arrange
    context = UserContext(user_id=123)
    context.add_message("user", "Message 1")
    context.add_message("assistant", "Message 2")
    context.add_message("user", "Message 3")

    # Act
    messages = context.get_messages(limit=2)

    # Assert
    assert len(messages) == 2
    assert messages[0].content == "Message 2"
    assert messages[1].content == "Message 3"


def test_user_context_clear():
    """Тест очистки UserContext."""
    # Arrange
    context = UserContext(user_id=123)
    context.add_message("user", "Message 1")
    context.add_message("user", "Message 2")

    # Act
    context.clear()

    # Assert
    assert len(context.messages) == 0


@pytest.fixture
def config(monkeypatch):
    """Фикстура конфигурации для тестов."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.test.com")
    monkeypatch.setenv("MAX_CONTEXT_MESSAGES", "10")
    return Config()


def test_context_manager_init(config):
    """Тест инициализации ContextManager."""
    # Act
    manager = ContextManager(config)

    # Assert
    assert manager.config == config
    assert len(manager.contexts) == 0


def test_add_message_creates_context(config):
    """Тест создания контекста при добавлении первого сообщения."""
    # Arrange
    manager = ContextManager(config)

    # Act
    manager.add_message(123, "user", "Hello")

    # Assert
    assert 123 in manager.contexts
    assert len(manager.contexts[123].messages) == 1


def test_add_message_multiple(config):
    """Тест добавления нескольких сообщений."""
    # Arrange
    manager = ContextManager(config)

    # Act
    manager.add_message(123, "user", "Message 1")
    manager.add_message(123, "assistant", "Message 2")
    manager.add_message(123, "user", "Message 3")

    # Assert
    assert len(manager.contexts[123].messages) == 3


def test_get_history_empty(config):
    """Тест получения пустой истории."""
    # Arrange
    manager = ContextManager(config)

    # Act
    history = manager.get_history(999)

    # Assert
    assert len(history) == 0


def test_get_history_with_messages(config):
    """Тест получения истории с сообщениями."""
    # Arrange
    manager = ContextManager(config)
    manager.add_message(123, "user", "Message 1")
    manager.add_message(123, "assistant", "Message 2")

    # Act
    history = manager.get_history(123)

    # Assert
    assert len(history) == 2
    assert history[0].content == "Message 1"
    assert history[1].content == "Message 2"


def test_clear_history(config):
    """Тест очистки истории."""
    # Arrange
    manager = ContextManager(config)
    manager.add_message(123, "user", "Message 1")
    manager.add_message(123, "user", "Message 2")

    # Act
    manager.clear_history(123)

    # Assert
    assert len(manager.contexts[123].messages) == 0


def test_trim_history(config, monkeypatch):
    """Тест обрезки истории при превышении лимита."""
    # Arrange
    monkeypatch.setenv("MAX_CONTEXT_MESSAGES", "3")
    config_small = Config()
    manager = ContextManager(config_small)

    # Act
    for i in range(5):
        manager.add_message(123, "user", f"Message {i + 1}")

    # Assert
    history = manager.get_history(123)
    assert len(history) == 3
    assert history[0].content == "Message 3"
    assert history[1].content == "Message 4"
    assert history[2].content == "Message 5"


def test_multiple_users(config):
    """Тест работы с несколькими пользователями."""
    # Arrange
    manager = ContextManager(config)

    # Act
    manager.add_message(123, "user", "User 1 message")
    manager.add_message(456, "user", "User 2 message")
    manager.add_message(123, "assistant", "Response to user 1")

    # Assert
    assert len(manager.contexts) == 2
    assert len(manager.get_history(123)) == 2
    assert len(manager.get_history(456)) == 1
