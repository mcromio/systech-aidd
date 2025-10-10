"""Клиент для работы с OpenAI LLM."""

import logging

from openai import AsyncOpenAI

from src.config import Config
from src.context_manager import Message

logger = logging.getLogger(__name__)


class LLMClient:
    """Клиент для работы с OpenAI API."""

    def __init__(self, config: Config, wikipedia_tool=None):
        """
        Инициализация LLM клиента.

        Args:
            config: Конфигурация приложения
            wikipedia_tool: Wikipedia tool (не используется в базовой версии)
        """
        self.config = config
        self.wikipedia_tool = wikipedia_tool

        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
        )
        logger.info(f"LLMClient инициализирован с моделью {config.openai_model}")

    async def get_response(self, messages: list[Message]) -> str | None:
        """
        Получить ответ от LLM (базовая версия без tools).

        Args:
            messages: История сообщений

        Returns:
            Ответ от LLM или None при ошибке
        """
        try:
            # Формируем запрос с системным промптом
            request_messages = [{"role": "system", "content": self.config.system_prompt}]

            # Добавляем историю диалога
            for msg in messages:
                request_messages.append({"role": msg.role, "content": msg.content})

            logger.debug(f"Отправка запроса к LLM: {len(request_messages)} сообщений")

            # Запрос к OpenAI API
            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=request_messages,
                temperature=0.7,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            logger.info("Получен ответ от LLM")
            return content

        except Exception as e:
            logger.error(f"Ошибка при обращении к LLM: {e}", exc_info=True)
            return None
