"""Управление историей диалогов пользователей."""

import logging
from typing import Literal

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.config import Config
from src.db.repositories import MessageRepository, UserRepository
from src.db.session import get_session

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """
    Сообщение в диалоге (Pydantic модель для обратной совместимости).

    Используется для передачи сообщений между компонентами.
    """

    role: Literal["user", "assistant", "system"]
    content: str


class ContextManager:
    """
    Менеджер контекста диалогов с персистентным хранилищем.

    S1: Заменили in-memory хранилище на PostgreSQL через репозитории.
    API остался без изменений для обратной совместимости.
    """

    def __init__(self, config: Config, session_factory: async_sessionmaker):
        """
        Инициализация менеджера контекста.

        Args:
            config: Конфигурация приложения
            session_factory: Фабрика сессий SQLAlchemy
        """
        self.config = config
        self.session_factory = session_factory
        logger.info("ContextManager инициализирован (с БД)")

    async def add_message(
        self, user_id: int, role: Literal["user", "assistant", "system"], content: str
    ) -> None:
        """
        Добавить сообщение в историю пользователя.

        S1: Сохраняет в БД вместо in-memory dict.

        Args:
            user_id: ID пользователя Telegram
            role: Роль отправителя (user/assistant/system)
            content: Содержимое сообщения
        """
        async with get_session(self.session_factory) as session:
            user_repo = UserRepository(session)
            message_repo = MessageRepository(session)

            # Получить или создать пользователя
            user, created = await user_repo.get_or_create_user(telegram_id=user_id)

            if created:
                logger.info(f"Создан новый пользователь: telegram_id={user_id}, db_id={user.id}")

            # Создать сообщение
            await message_repo.create_message(
                user_id=user.id,  # Используем internal DB id
                role=role,
                content=content,
            )

            logger.debug(f"Добавлено сообщение для telegram_id={user_id}: {role}")

    async def get_history(self, user_id: int) -> list[Message]:
        """
        Получить историю диалога пользователя.

        S1: Читает из БД вместо in-memory dict.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Список сообщений (последние N)
        """
        async with get_session(self.session_factory) as session:
            user_repo = UserRepository(session)
            message_repo = MessageRepository(session)

            # Получить пользователя
            user = await user_repo.get_by_telegram_id(user_id)

            if not user:
                logger.debug(f"История для telegram_id={user_id} пуста (пользователь не найден)")
                return []

            # Получить историю сообщений
            db_messages = await message_repo.get_user_history(
                user_id=user.id,
                limit=self.config.max_context_messages,
            )

            # Конвертировать в Pydantic модели для обратной совместимости
            messages = [
                Message(role=msg.role, content=msg.content)  # type: ignore[arg-type]
                for msg in db_messages
            ]

            logger.debug(f"Получена история для telegram_id={user_id}: {len(messages)} сообщений")

            return messages

    async def clear_history(self, user_id: int) -> None:
        """
        Очистить историю диалога пользователя (soft delete).

        S1: Soft delete в БД вместо очистки in-memory dict.

        Args:
            user_id: ID пользователя Telegram
        """
        async with get_session(self.session_factory) as session:
            user_repo = UserRepository(session)
            message_repo = MessageRepository(session)

            # Получить пользователя
            user = await user_repo.get_by_telegram_id(user_id)

            if not user:
                logger.debug(f"Нечего очищать для telegram_id={user_id} (пользователь не найден)")
                return

            # Soft delete всех сообщений
            deleted_count = await message_repo.soft_delete_user_messages(user_id=user.id)

            logger.info(
                f"История telegram_id={user_id} очищена (soft delete): {deleted_count} сообщений"
            )
