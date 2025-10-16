"""Настройка SQLAlchemy engine и session factory."""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import Config

logger = logging.getLogger(__name__)


def create_engine(config: Config) -> AsyncEngine:
    """
    Создать async SQLAlchemy engine.

    Args:
        config: Конфигурация приложения

    Returns:
        AsyncEngine для подключения к БД
    """
    engine = create_async_engine(
        config.database_url,
        echo=config.database_echo,
        pool_size=config.database_pool_size,
        max_overflow=10,
        pool_pre_ping=True,  # Проверка соединений перед использованием
        pool_recycle=3600,  # Переподключение каждый час
    )

    logger.info(
        f"SQLAlchemy engine создан: "
        f"pool_size={config.database_pool_size}, "
        f"echo={config.database_echo}"
    )

    return engine


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Создать фабрику сессий.

    Args:
        engine: SQLAlchemy async engine

    Returns:
        Фабрика для создания сессий
    """
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Не сбрасывать объекты после commit
        autoflush=False,  # Ручное управление flush
        autocommit=False,  # Явные транзакции
    )

    logger.info("Session factory создана")

    return session_factory


async def check_connection(engine: AsyncEngine) -> bool:
    """
    Проверить подключение к БД.

    Args:
        engine: SQLAlchemy async engine

    Returns:
        True если подключение успешно

    Raises:
        Exception: Если не удалось подключиться
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Подключение к БД успешно")
        return True
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        raise


async def close_engine(engine: AsyncEngine) -> None:
    """
    Закрыть engine и освободить ресурсы.

    Args:
        engine: SQLAlchemy async engine
    """
    await engine.dispose()
    logger.info("SQLAlchemy engine закрыт")
