"""Репозиторий для работы с сообщениями."""

import logging
from datetime import datetime
from typing import Literal

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Message
from src.db.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class MessageRepository(BaseRepository[Message]):
    """
    Репозиторий для работы с сообщениями диалогов.

    Предоставляет методы для:
    - Создания сообщения
    - Получения истории пользователя
    - Soft delete сообщений
    - Подсчёта сообщений
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория сообщений.

        Args:
            session: Async сессия БД
        """
        super().__init__(Message, session)

    async def create_message(
        self,
        user_id: int,
        role: Literal["user", "assistant", "system"],
        content: str,
    ) -> Message:
        """
        Создать новое сообщение.

        Args:
            user_id: ID пользователя (internal DB id)
            role: Роль отправителя
            content: Содержимое сообщения

        Returns:
            Созданное сообщение
        """
        message = Message(
            user_id=user_id,
            role=role,
            content=content,
            content_length=len(content),
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)

        logger.debug(
            f"Создано сообщение: "
            f"id={message.id}, user_id={user_id}, role={role}, "
            f"length={len(content)}"
        )

        return message

    async def get_user_history(
        self,
        user_id: int,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> list[Message]:
        """
        Получить историю сообщений пользователя.

        Args:
            user_id: ID пользователя (internal DB id)
            limit: Количество последних сообщений
            include_deleted: Включать удалённые сообщения

        Returns:
            Список сообщений (от старых к новым)
        """
        stmt = select(Message).where(Message.user_id == user_id)

        if not include_deleted:
            stmt = stmt.where(Message.is_deleted == False)  # noqa: E712

        stmt = stmt.order_by(Message.created_at.desc()).limit(limit)

        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())

        # Возвращаем в хронологическом порядке (старые → новые)
        messages.reverse()

        logger.debug(
            f"Получена история для user_id={user_id}: {len(messages)} сообщений (limit={limit})"
        )

        return messages

    async def soft_delete_user_messages(self, user_id: int) -> int:
        """
        Мягкое удаление всех активных сообщений пользователя.

        Args:
            user_id: ID пользователя (internal DB id)

        Returns:
            Количество удалённых сообщений
        """
        stmt = (
            update(Message)
            .where(Message.user_id == user_id, Message.is_deleted == False)  # noqa: E712
            .values(is_deleted=True, deleted_at=datetime.utcnow())
            .execution_options(synchronize_session="fetch")
        )

        result = await self.session.execute(stmt)
        await self.session.flush()

        deleted_count = result.rowcount or 0

        logger.info(f"Soft delete для user_id={user_id}: {deleted_count} сообщений")

        return deleted_count

    async def soft_delete_message(self, message_id: int) -> bool:
        """
        Мягкое удаление одного сообщения.

        Args:
            message_id: ID сообщения

        Returns:
            True если сообщение было удалено
        """
        message = await self.get_by_id(message_id)
        if not message or message.is_deleted:
            return False

        message.soft_delete()
        await self.session.flush()

        logger.debug(f"Soft delete для message_id={message_id}")

        return True

    async def restore_message(self, message_id: int) -> bool:
        """
        Восстановить удалённое сообщение.

        Args:
            message_id: ID сообщения

        Returns:
            True если сообщение было восстановлено
        """
        message = await self.get_by_id(message_id)
        if not message or not message.is_deleted:
            return False

        message.restore()
        await self.session.flush()

        logger.debug(f"Восстановлено сообщение message_id={message_id}")

        return True

    async def count_user_messages(self, user_id: int, include_deleted: bool = False) -> int:
        """
        Подсчитать количество сообщений пользователя.

        Args:
            user_id: ID пользователя (internal DB id)
            include_deleted: Включать удалённые сообщения

        Returns:
            Количество сообщений
        """
        stmt = select(func.count(Message.id)).where(Message.user_id == user_id)

        if not include_deleted:
            stmt = stmt.where(Message.is_deleted == False)  # noqa: E712

        result = await self.session.execute(stmt)
        count = result.scalar_one()

        return count

    async def get_total_messages(self, include_deleted: bool = False) -> int:
        """
        Подсчитать общее количество сообщений.

        Args:
            include_deleted: Включать удалённые сообщения

        Returns:
            Общее количество сообщений
        """
        stmt = select(func.count(Message.id))

        if not include_deleted:
            stmt = stmt.where(Message.is_deleted == False)  # noqa: E712

        result = await self.session.execute(stmt)
        count = result.scalar_one()

        return count

    async def get_average_content_length(self, user_id: int | None = None) -> float:
        """
        Получить среднюю длину сообщений.

        Args:
            user_id: ID пользователя (опционально, для конкретного пользователя)

        Returns:
            Средняя длина сообщения
        """
        stmt = select(func.avg(Message.content_length)).where(
            Message.is_deleted == False  # noqa: E712
        )

        if user_id is not None:
            stmt = stmt.where(Message.user_id == user_id)

        result = await self.session.execute(stmt)
        avg_length = result.scalar_one() or 0.0

        return float(avg_length)
