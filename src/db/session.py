"""Утилиты для работы с сессиями."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager для получения сессии БД.

    Автоматически закрывает сессию и откатывает транзакцию при ошибке.

    Args:
        session_factory: Фабрика для создания сессий

    Yields:
        AsyncSession для работы с БД

    Example:
        >>> async with get_session(session_factory) as session:
        >>>     user = await session.get(User, 1)
    """
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка в транзакции, откат: {e}")
        raise
    finally:
        await session.close()
