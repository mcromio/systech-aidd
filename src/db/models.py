"""SQLAlchemy модели для БД."""

import logging
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

logger = logging.getLogger(__name__)


class User(Base):
    """
    Модель пользователя Telegram.

    Attributes:
        id: Внутренний ID (автоинкремент)
        telegram_id: ID пользователя в Telegram (уникальный)
        username: Username в Telegram (может быть None)
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        created_at: Дата регистрации
        last_seen_at: Дата последней активности
        messages: Связь с сообщениями пользователя
    """

    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Telegram данные
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
        comment="Telegram User ID",
    )
    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Telegram username (может быть None)",
    )
    first_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Имя пользователя",
    )
    last_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Фамилия пользователя",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата регистрации",
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата последней активности",
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Строковое представление пользователя."""
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"

    def update_last_seen(self) -> None:
        """Обновить время последней активности."""
        self.last_seen_at = datetime.utcnow()


class Message(Base):
    """
    Модель сообщения в диалоге.

    Attributes:
        id: Внутренний ID сообщения (автоинкремент)
        user_id: ID пользователя (FK к users)
        role: Роль отправителя ('user', 'assistant', 'system')
        content: Содержимое сообщения
        content_length: Длина сообщения в символах
        created_at: Дата создания сообщения
        is_deleted: Флаг soft delete
        deleted_at: Дата удаления (soft delete)
        user: Связь с пользователем
    """

    __tablename__ = "messages"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID пользователя",
    )

    # Message данные
    role: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("role IN ('user', 'assistant', 'system')"),
        nullable=False,
        comment="Роль отправителя",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Содержимое сообщения",
    )
    content_length: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Длина сообщения в символах",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Дата создания",
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        server_default="false",
        nullable=False,
        index=True,
        comment="Флаг мягкого удаления",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата удаления",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="messages")

    def __repr__(self) -> str:
        """Строковое представление сообщения."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return (
            f"<Message(id={self.id}, "
            f"user_id={self.user_id}, "
            f"role={self.role}, "
            f"content='{content_preview}')>"
        )

    def soft_delete(self) -> None:
        """
        Мягкое удаление сообщения.

        Устанавливает is_deleted=True и deleted_at=NOW().
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        logger.debug(f"Сообщение {self.id} помечено как удаленное")

    def restore(self) -> None:
        """
        Восстановить удаленное сообщение.

        Сбрасывает is_deleted=False и deleted_at=None.
        """
        self.is_deleted = False
        self.deleted_at = None
        logger.debug(f"Сообщение {self.id} восстановлено")

    @property
    def is_active(self) -> bool:
        """Проверить, активно ли сообщение (не удалено)."""
        return not self.is_deleted
