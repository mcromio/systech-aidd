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
        default="gpt-4.1-mini",
        description="Модель LLM",
    )
    openai_timeout: float = Field(
        default=60.0,
        ge=1.0,
        description="Таймаут для запросов к OpenAI (секунды)",
    )

    # LLM параметры
    llm_max_tool_iterations: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Максимум итераций tool calls",
    )
    llm_max_websearch_calls: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Максимум веб-запросов за диалог",
    )
    llm_max_tokens_with_tools: int = Field(
        default=10000,
        ge=1000,
        description="Максимум токенов ответа с tools",
    )
    llm_max_tokens_no_tools: int = Field(
        default=12000,
        ge=1000,
        description="Максимум токенов ответа без tools",
    )

    # WebSearch параметры
    websearch_default_results: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Дефолтное количество результатов поиска",
    )
    websearch_max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Максимум результатов поиска",
    )
    websearch_max_body_length: int = Field(
        default=200,
        ge=50,
        description="Максимальная длина описания результата",
    )

    # Wikipedia параметры
    wikipedia_max_summary_length: int = Field(
        default=500,
        ge=100,
        description="Максимальная длина summary",
    )
    wikipedia_user_agent: str = Field(
        default="LLM-Assistant-Bot/1.0",
        description="User agent для Wikipedia API",
    )

    # Роль бота (TDD: Iteration 7)
    system_prompt_file: str = Field(
        default=str(PROJECT_ROOT / "prompts" / "default.txt"),
        description="Путь к файлу системного промпта",
    )
    role_name: str = Field(
        default="AI Assistant",
        description="Название роли бота",
    )
    role_description: str = Field(
        default="Универсальный ИИ-ассистент",
        description="Краткое описание роли",
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

    # Database Configuration (S1: Persistent Storage)
    database_url: str = Field(
        default="postgresql+asyncpg://llm_user:llm_password_dev@localhost:5432/llm_assistant",
        description="PostgreSQL connection URL",
    )
    database_pool_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Размер connection pool",
    )
    database_echo: bool = Field(
        default=False,
        description="Логировать SQL запросы (для отладки)",
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

    def __init__(self, **kwargs: object) -> None:
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
                        os.environ[key] = env_vars[key]  # type: ignore[assignment]

        super().__init__(**kwargs)  # type: ignore[arg-type]

    def model_post_init(self, __context: object) -> None:
        """Загрузка системного промпта из файла после инициализации (TDD: Iteration 7)."""
        prompt_path = Path(self.system_prompt_file)
        if prompt_path.exists():
            self.system_prompt = prompt_path.read_text(encoding="utf-8")
            logger.info(f"Системный промпт загружен из файла: {self.system_prompt_file}")
        else:
            raise FileNotFoundError(f"System prompt file not found: {self.system_prompt_file}")

    def validate_config(self) -> None:
        """Валидация конфигурации при старте."""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN обязателен")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY обязателен")
        if not self.openai_proxy_url:
            raise ValueError("OPENAI_PROXY_URL обязателен")

        logger.info("Конфигурация успешно загружена и проверена")
