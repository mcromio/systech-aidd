"""Репозитории для работы с БД."""

from src.db.repositories.message_repository import MessageRepository
from src.db.repositories.user_repository import UserRepository

__all__ = ["MessageRepository", "UserRepository"]
