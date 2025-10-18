"""Репозиторий для работы с пользователями."""

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.db.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """
    Репозиторий для работы с пользователями Telegram.

    Предоставляет методы для:
    - Создания пользователя
    - Получения или создания пользователя (get_or_create)
    - Обновления времени последней активности
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория пользователей.

        Args:
            session: Async сессия БД
        """
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """
        Получить пользователя по Telegram ID.

        Args:
            telegram_id: ID пользователя в Telegram

        Returns:
            Объект User или None если не найден
        """
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> tuple[User, bool]:
        """
        Получить существующего пользователя или создать нового.

        Args:
            telegram_id: ID пользователя в Telegram
            username: Username пользователя (опционально)
            first_name: Имя пользователя (опционально)
            last_name: Фамилия пользователя (опционально)

        Returns:
            Tuple (User, created) где created=True если пользователь создан
        """
        # Пытаемся найти существующего пользователя
        user = await self.get_by_telegram_id(telegram_id)

        if user:
            # Обновляем профильные данные из Telegram
            if username is not None:
                user.username = username
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name

            # Обновляем last_seen_at
            user.update_last_seen()
            await self.session.flush()
            logger.debug(f"Пользователь {telegram_id} обновлен")
            return user, False

        # Создаём нового пользователя
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            last_seen_at=datetime.now(UTC),
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        logger.info(
            f"Создан новый пользователь: "
            f"id={user.id}, telegram_id={telegram_id}, username={username}"
        )

        return user, True

    async def update_last_seen(self, telegram_id: int) -> User | None:
        """
        Обновить время последней активности пользователя.

        Args:
            telegram_id: ID пользователя в Telegram

        Returns:
            Обновлённый объект User или None
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.update_last_seen()
            await self.session.flush()
            logger.debug(f"Обновлён last_seen для пользователя {telegram_id}")
        return user

    async def count_users(self) -> int:
        """
        Подсчитать общее количество пользователей.

        Returns:
            Количество пользователей
        """
        from sqlalchemy import func

        stmt = select(func.count(User.id))
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count
