"""Точка входа приложения."""

import asyncio
import logging
import sys

from src.bot import TelegramBot
from src.config import Config
from src.context_manager import ContextManager
from src.handlers import MessageHandler
from src.llm_client import LLMClient
from src.wikipedia_tool import WikipediaTool

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Настройка логирования приложения.

    Args:
        log_level: Уровень логирования
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Отключаем лишние логи от библиотек
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("aiogram").setLevel(logging.INFO)


async def main() -> None:
    """Главная функция приложения."""
    # 1. Загрузка конфигурации
    config = Config()
    config.validate_config()

    # 2. Настройка логирования
    setup_logging(config.log_level)

    logger.info("=== Запуск LLM-ассистента ===")
    logger.info(f"Модель: {config.openai_model}")
    logger.info(f"Макс. контекст: {config.max_context_messages}")

    # 3. Создание компонентов
    context_manager = ContextManager(config)
    wikipedia_tool = WikipediaTool()
    llm_client = LLMClient(config, wikipedia_tool)
    message_handler = MessageHandler(config, context_manager, llm_client)

    # 4. Запуск бота
    bot = TelegramBot(config, message_handler)
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)
