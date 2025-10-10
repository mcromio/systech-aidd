"""Конфигурация приложения."""

import logging
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """Конфигурация LLM-ассистента."""

    # Telegram
    telegram_bot_token: str = Field(..., description="Токен Telegram бота")

    # OpenAI
    openai_api_key: str = Field(..., description="API ключ OpenAI")
    openai_base_url: str = Field(..., description="URL прокси для OpenAI")
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Модель LLM",
    )

    # Поведение
    system_prompt: str = Field(
        default="You are a helpful assistant. Answer user questions politely and informatively.",
        description="Системный промпт для LLM",
    )
    max_context_messages: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Максимум сообщений в истории",
    )

    # Логирование
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Уровень логирования",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def validate_config(self) -> None:
        """Валидация конфигурации при старте."""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN обязателен")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY обязателен")
        if not self.openai_base_url:
            raise ValueError("OPENAI_BASE_URL обязателен")

        logger.info("Конфигурация успешно загружена и проверена")
