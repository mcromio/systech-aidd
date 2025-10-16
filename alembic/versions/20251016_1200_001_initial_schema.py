"""Initial schema: users and messages tables

Revision ID: 001_initial
Revises:
Create Date: 2025-10-16 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Создание таблицы users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "telegram_id",
            sa.BigInteger(),
            nullable=False,
            comment="Telegram User ID",
        ),
        sa.Column(
            "username",
            sa.String(length=255),
            nullable=True,
            comment="Telegram username (может быть None)",
        ),
        sa.Column(
            "first_name",
            sa.String(length=255),
            nullable=True,
            comment="Имя пользователя",
        ),
        sa.Column(
            "last_name",
            sa.String(length=255),
            nullable=True,
            comment="Фамилия пользователя",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата регистрации",
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Дата последней активности",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_id"),
    )

    # Индексы для users
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=False)

    # Создание таблицы messages
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
            comment="ID пользователя",
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            comment="Роль отправителя",
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
            comment="Содержимое сообщения",
        ),
        sa.Column(
            "content_length",
            sa.Integer(),
            nullable=False,
            comment="Длина сообщения в символах",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата создания",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default="false",
            nullable=False,
            comment="Флаг мягкого удаления",
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Дата удаления",
        ),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Индексы для messages
    op.create_index("ix_messages_user_id", "messages", ["user_id"], unique=False)
    op.create_index("ix_messages_created_at", "messages", ["created_at"], unique=False)
    op.create_index("ix_messages_is_deleted", "messages", ["is_deleted"], unique=False)

    # Композитный индекс для get_history запросов
    op.create_index(
        "idx_messages_user_id_created_at",
        "messages",
        ["user_id", sa.text("created_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Удаление таблиц в обратном порядке
    op.drop_index("idx_messages_user_id_created_at", table_name="messages")
    op.drop_index("ix_messages_is_deleted", table_name="messages")
    op.drop_index("ix_messages_created_at", table_name="messages")
    op.drop_index("ix_messages_user_id", table_name="messages")
    op.drop_table("messages")

    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
