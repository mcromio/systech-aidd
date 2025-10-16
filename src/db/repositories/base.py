"""Базовый класс для репозиториев."""

import logging
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Base

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий с CRUD операциями.

    Attributes:
        model: SQLAlchemy модель
        session: Async сессия БД
    """

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """
        Инициализация репозитория.

        Args:
            model: SQLAlchemy модель
            session: Async сессия БД
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        """
        Получить объект по ID.

        Args:
            id: ID объекта

        Returns:
            Объект модели или None
        """
        return await self.session.get(self.model, id)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        """
        Получить все объекты с пагинацией.

        Args:
            limit: Количество объектов
            offset: Смещение

        Returns:
            Список объектов
        """
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelType:
        """
        Создать новый объект.

        Args:
            **kwargs: Параметры для создания объекта

        Returns:
            Созданный объект
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType, **kwargs: Any) -> ModelType:
        """
        Обновить объект.

        Args:
            instance: Объект для обновления
            **kwargs: Новые значения полей

        Returns:
            Обновленный объект
        """
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        """
        Удалить объект (физическое удаление).

        Args:
            instance: Объект для удаления
        """
        await self.session.delete(instance)
        await self.session.flush()

    async def commit(self) -> None:
        """Сохранить изменения в БД."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Откатить транзакцию."""
        await self.session.rollback()
