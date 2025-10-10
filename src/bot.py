"""Telegram бот."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from src.config import Config
from src.handlers import MessageHandler

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram бот на основе aiogram."""

    def __init__(self, config: Config, message_handler: MessageHandler):
        """
        Инициализация Telegram бота.

        Args:
            config: Конфигурация приложения
            message_handler: Обработчик сообщений
        """
        self.config = config
        self.message_handler = message_handler

        self.bot = Bot(token=config.telegram_bot_token)
        self.dp = Dispatcher()

        logger.info("TelegramBot инициализирован")

    def register_handlers(self) -> None:
        """Регистрация обработчиков команд и сообщений."""
        # Команды
        self.dp.message.register(
            self.message_handler.handle_start,
            Command(commands=["start"]),
        )
        self.dp.message.register(
            self.message_handler.handle_help,
            Command(commands=["help"]),
        )
        self.dp.message.register(
            self.message_handler.handle_reset,
            Command(commands=["reset"]),
        )

        # Текстовые сообщения (все что не команды)
        self.dp.message.register(self.message_handler.handle_message)

        logger.info("Handlers зарегистрированы")

    async def start(self) -> None:
        """Запуск бота через infinite polling."""
        logger.info("Запуск бота...")
        self.register_handlers()

        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
            raise
        finally:
            await self.bot.session.close()
