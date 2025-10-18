"""Точка входа приложения."""

import asyncio
import logging
import sys

from src.bot import TelegramBot
from src.config import Config
from src.context_manager import ContextManager
from src.db.engine import check_connection, close_engine, create_engine, get_session_factory
from src.handlers import MessageHandler
from src.llm_client import LLMClient

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
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if logging.getLogger().level == logging.DEBUG else logging.WARNING
    )


async def main() -> None:
    """Главная функция приложения."""
    # 1. Загрузка конфигурации
    config = Config()
    config.validate_config()

    # 2. Настройка логирования
    setup_logging(config.log_level)

    logger.info("=== Запуск LLM-ассистента (S1: с БД) ===")
    logger.info(f"Модель: {config.llm_model}")
    logger.info(f"Макс. контекст: {config.max_context_messages}")
    logger.info(f"База данных: {config.database_url.split('@')[-1]}")  # Без credentials

    # 3. Инициализация БД (S1: Persistent Storage)
    logger.info("Инициализация подключения к БД...")
    engine = create_engine(config)

    try:
        # Проверка подключения
        await check_connection(engine)

        # Создание session factory
        session_factory = get_session_factory(engine)

        logger.info("БД готова к работе")

        # 4. Создание компонентов
        context_manager = ContextManager(config, session_factory)  # S1: добавлен session_factory
        llm_client = LLMClient(config)  # tools создаются автоматически
        message_handler = MessageHandler(config, context_manager, llm_client)

        # 5. Запуск бота
        bot = TelegramBot(config, message_handler)

        try:
            await bot.start()
        finally:
            # Graceful shutdown
            logger.info("Остановка приложения...")
            await close_engine(engine)
            logger.info("БД отключена")

    except Exception as e:
        logger.error(f"Ошибка при работе с БД: {e}")
        await close_engine(engine)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)
