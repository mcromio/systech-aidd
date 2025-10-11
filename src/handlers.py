"""Обработчики команд и сообщений Telegram бота."""

import logging

from aiogram import types

from src.config import Config
from src.context_manager import ContextManager
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)


class MessageHandler:
    """Обработчик сообщений от пользователей."""

    def __init__(
        self,
        config: Config,
        context_manager: ContextManager,
        llm_client: LLMClient,
    ):
        """
        Инициализация обработчика сообщений.

        Args:
            config: Конфигурация приложения
            context_manager: Менеджер контекста диалогов
            llm_client: Клиент для работы с LLM
        """
        self.config = config
        self.context_manager = context_manager
        self.llm_client = llm_client
        logger.info("MessageHandler инициализирован")

    async def handle_start(self, message: types.Message) -> None:
        """
        Обработка команды /start.

        Args:
            message: Сообщение от пользователя
        """
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.info(f"Команда /start от пользователя {user_id}")

        welcome_text = (
            "👋 Привет! Я LLM-ассистент.\n\n"
            "Я могу отвечать на ваши вопросы и искать информацию в Wikipedia.\n\n"
            "Доступные команды:\n"
            "/help - справка\n"
            "/role - узнать мою роль\n"
            "/reset - очистить историю диалога"
        )

        await message.answer(welcome_text)

    async def handle_help(self, message: types.Message) -> None:
        """
        Обработка команды /help.

        Args:
            message: Сообщение от пользователя
        """
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.info(f"Команда /help от пользователя {user_id}")

        help_text = (
            "📚 Справка по использованию:\n\n"
            "Просто напишите мне сообщение, и я постараюсь ответить!\n\n"
            "Я умею:\n"
            "• Отвечать на вопросы\n"
            "• Искать информацию в Wikipedia\n"
            "• Запоминать контекст диалога\n\n"
            "Команды:\n"
            "/start - начать диалог\n"
            "/help - эта справка\n"
            "/role - узнать мою роль\n"
            "/reset - очистить историю диалога"
        )

        await message.answer(help_text)

    async def handle_reset(self, message: types.Message) -> None:
        """
        Обработка команды /reset (очистка истории).

        Args:
            message: Сообщение от пользователя
        """
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.info(f"Команда /reset от пользователя {user_id}")

        self.context_manager.clear_history(user_id)

        reset_text = "🗑 История диалога очищена. Начнем сначала!"
        await message.answer(reset_text)

    async def handle_role(self, message: types.Message) -> None:
        """
        Обработка команды /role (отображение роли бота) - TDD: Iteration 7.

        Args:
            message: Сообщение от пользователя
        """
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.info(f"Команда /role от пользователя {user_id}")

        role_info = (
            f"🤖 Моя роль\n\n"
            f"Название: {self.config.role_name}\n\n"
            f"Описание: {self.config.role_description}\n\n"
            f"Я специализируюсь на выполнении конкретных задач в рамках своей роли.\n"
            f"Системный промпт: {self.config.system_prompt_file}"
        )

        await message.answer(role_info)

    async def handle_message(self, message: types.Message) -> None:
        """
        Обработка текстовых сообщений.

        Args:
            message: Сообщение от пользователя
        """
        if not message.from_user or not message.text:
            return
        user_id = message.from_user.id
        user_text = message.text

        logger.info(f"Сообщение от пользователя {user_id}: {user_text[:50]}...")

        try:
            # Добавляем сообщение пользователя в контекст
            self.context_manager.add_message(user_id, "user", user_text)

            # Получаем историю диалога
            history = self.context_manager.get_history(user_id)

            # Получаем ответ от LLM
            response = await self.llm_client.get_response(history)

            if response:
                # Добавляем ответ ассистента в контекст
                self.context_manager.add_message(user_id, "assistant", response)

                # Отправляем ответ пользователю
                await message.answer(response)
                logger.info(f"Ответ отправлен пользователю {user_id}")
            else:
                error_text = "Извините, произошла ошибка. Попробуйте позже."
                await message.answer(error_text)
                logger.warning(f"LLM вернул None для пользователя {user_id}")

        except Exception as e:
            logger.error(
                f"Ошибка при обработке сообщения от {user_id}: {e}",
                exc_info=True,
            )
            error_text = "Произошла ошибка при обработке сообщения. Попробуйте позже."
            await message.answer(error_text)
