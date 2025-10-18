"""Обработчики команд и сообщений Telegram бота."""

import logging
import re

from aiogram import types

from src.config import Config
from src.context_manager import ContextManager
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)


async def fetch_url_content(url: str, max_length: int = 3000) -> str | None:
    """
    Получить содержимое URL с умным парсингом.

    Args:
        url: URL для загрузки
        max_length: Максимальная длина контента

    Returns:
        Текстовое содержимое или None
    """
    try:
        import httpx
        from bs4 import BeautifulSoup

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200:
                # Парсим HTML с BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")

                # Удаляем скрипты и стили
                for tag in soup(["script", "style"]):
                    tag.decompose()

                # Пытаемся получить основной контент
                text_parts = []

                # Ищем заголовок страницы
                title = soup.find("title")
                if title:
                    text_parts.append(f"Заголовок: {title.get_text().strip()}")

                # Ищем meta description
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc:
                    desc = meta_desc.get("content", "").strip()
                    if desc:
                        text_parts.append(f"Описание: {desc}")

                # Ищем основной контент в main, article, или content
                main_content = soup.find(["main", "article", "div[class*='content']"])
                if not main_content:
                    main_content = soup.body if soup.body else soup

                # Извлекаем текст
                if main_content:
                    paragraphs = main_content.find_all(["p", "h1", "h2", "h3", "li"])
                    for para in paragraphs[:15]:  # Ограничиваем количество элементов
                        text = para.get_text().strip()
                        if text and len(text) > 20:  # Только значимые куски
                            text_parts.append(text)

                # Собираем результат
                full_text = "\n".join(text_parts)
                full_text = re.sub(r"\s+", " ", full_text).strip()

                if full_text:
                    return full_text[:max_length]

    except Exception as e:
        logger.warning(f"Не удалось загрузить URL {url}: {e}")
    return None


def extract_urls(text: str) -> list[str]:
    """
    Извлечь URL из текста.

    Args:
        text: Текст для анализа

    Returns:
        Список найденных URL
    """
    url_pattern = r"https?://[^\s]+"
    return re.findall(url_pattern, text)


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

        await self.context_manager.clear_history(user_id)

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
            # Проверяем наличие URL в сообщении
            urls = extract_urls(user_text)
            enriched_text = user_text

            if urls:
                logger.info(f"Найдены URL: {urls}")
                url_contents = []

                for url in urls:
                    content = await fetch_url_content(url)
                    if content:
                        url_contents.append(f"[Содержимое из {url}]:\n{content}")
                        logger.info(f"Успешно загружено содержимое из {url}")

                if url_contents:
                    enriched_text = (
                        f"{user_text}\n\n📄 Информация со ссылок:\n{chr(10).join(url_contents)}"
                    )

            # Добавляем сообщение пользователя в контекст (с обогащенным текстом)
            await self.context_manager.add_message(
                user_id,
                "user",
                enriched_text,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
            )

            # Получаем историю диалога
            history = await self.context_manager.get_history(user_id)

            # Получаем ответ от LLM
            response = await self.llm_client.get_response(history)

            if response:
                # Добавляем ответ ассистента в контекст
                await self.context_manager.add_message(user_id, "assistant", response)

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
