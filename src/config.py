"""Конфигурация приложения."""

import logging
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Определяем корневую директорию проекта
PROJECT_ROOT = Path(__file__).parent.parent


class Config(BaseSettings):
    """Конфигурация LLM-ассистента."""

    # Telegram
    telegram_bot_token: str = Field(..., description="Токен Telegram бота")

    # OpenAI
    openai_api_key: str = Field(..., description="API ключ OpenAI")
    openai_proxy_url: str = Field(..., description="URL прокси для OpenAI")
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Модель LLM",
    )
    openai_timeout: float = Field(
        default=30.0,
        ge=1.0,
        description="Таймаут для запросов к OpenAI (секунды)",
    )

    # Поведение
    system_prompt: str = Field(
        default=(
            "You are a helpful assistant. Answer user questions politely and informatively.\n\n"
            "ВАЖНО: ВСЕГДА указывай источники информации в своих ответах:\n"
            "- Для информации из Wikipedia: добавляй ссылку в конце ответа\n"
            "- Для информации из интернета: указывай источники с URL\n"
            "- Для текущей даты/времени: указывай часовой пояс\n"
            "- Для общих знаний без поиска: укажи 'на основе общеизвестных фактов'\n\n"
            "Формат цитирования:\n"
            "📚 Источник: [Название](URL) - для Wikipedia и веб-поиска\n"
            "🕐 Источник: Текущее время в [часовой пояс] - для даты/времени\n\n"
            "СТРОГОЕ ОГРАНИЧЕНИЕ: Делай МАКСИМУМ 1-2 веб-запроса (web_search) за весь диалог. "
            "Используй полученную информацию максимально эффективно. Не делай множественные запросы к разным источникам - выбери 1-2 самых релевантных."
        ),
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
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
    )

    def __init__(self, **kwargs):
        """Инициализация с приоритетом .env над системными переменными."""
        # Читаем .env файл напрямую и переопределяем ТОЛЬКО если
        # переменная из системного окружения ОТЛИЧАЕТСЯ от .env
        # (это означает что она не из монkеypatch в тестах)
        import os

        from dotenv import dotenv_values

        env_path = PROJECT_ROOT / ".env"
        if env_path.exists() and not kwargs:  # Только если не передаются аргументы напрямую
            env_vars = dotenv_values(env_path)
            # Переопределяем только проблемные ключи (OPENAI_API_KEY)
            for key in ["OPENAI_API_KEY"]:
                if key in env_vars and env_vars[key]:
                    # Проверяем, что в системе другое значение (старый ключ)
                    if key in os.environ and os.environ[key] != env_vars[key]:
                        logger.debug(
                            f"Переопределение {key} из .env (было в системе другое значение)"
                        )
                        os.environ[key] = env_vars[key]

        super().__init__(**kwargs)

    def validate_config(self) -> None:
        """Валидация конфигурации при старте."""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN обязателен")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY обязателен")
        if not self.openai_proxy_url:
            raise ValueError("OPENAI_PROXY_URL обязателен")

        logger.info("Конфигурация успешно загружена и проверена")
