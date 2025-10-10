"""Управление историей диалогов пользователей."""

import logging
from typing import Literal

from pydantic import BaseModel

from src.config import Config

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Сообщение в диалоге."""

    role: Literal["user", "assistant", "system"]
    content: str


class UserContext(BaseModel):
    """Контекст диалога пользователя."""

    user_id: int
    messages: list[Message] = []

    def add_message(self, role: str, content: str) -> None:
        """Добавить сообщение в историю."""
        self.messages.append(Message(role=role, content=content))

    def get_messages(self, limit: int) -> list[Message]:
        """Получить последние N сообщений."""
        return self.messages[-limit:] if limit > 0 else self.messages

    def clear(self) -> None:
        """Очистить историю."""
        self.messages = []


class ContextManager:
    """Менеджер контекста диалогов."""

    def __init__(self, config: Config):
        """
        Инициализация менеджера контекста.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.contexts: dict[int, UserContext] = {}
        logger.info("ContextManager инициализирован")

    def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в историю пользователя.

        Args:
            user_id: ID пользователя Telegram
            role: Роль отправителя (user/assistant)
            content: Содержимое сообщения
        """
        if user_id not in self.contexts:
            self.contexts[user_id] = UserContext(user_id=user_id)
            logger.info(f"Создан новый контекст для пользователя {user_id}")

        self.contexts[user_id].add_message(role, content)
        self._trim_history(user_id)
        logger.debug(f"Добавлено сообщение для пользователя {user_id}: {role}")

    def get_history(self, user_id: int) -> list[Message]:
        """
        Получить историю диалога пользователя.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Список сообщений (последние N)
        """
        if user_id not in self.contexts:
            logger.debug(f"История для пользователя {user_id} пуста")
            return []

        return self.contexts[user_id].get_messages(self.config.max_context_messages)

    def clear_history(self, user_id: int) -> None:
        """
        Очистить историю диалога пользователя.

        Args:
            user_id: ID пользователя Telegram
        """
        if user_id in self.contexts:
            self.contexts[user_id].clear()
            logger.info(f"История пользователя {user_id} очищена")

    def _trim_history(self, user_id: int) -> None:
        """
        Обрезать историю до максимального размера.

        Args:
            user_id: ID пользователя Telegram
        """
        context = self.contexts[user_id]
        max_messages = self.config.max_context_messages

        if len(context.messages) > max_messages:
            context.messages = context.messages[-max_messages:]
            logger.debug(f"История пользователя {user_id} обрезана до {max_messages}")
