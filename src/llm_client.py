"""Фасад для работы с OpenAI LLM (обратная совместимость)."""

import logging

from src.config import Config
from src.context_manager import Message
from src.llm import OpenAIClient, ToolOrchestrator
from src.tools import DateTimeTool, Tool, WebSearchTool, WikipediaTool

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Фасад для работы с LLM (обратная совместимость).

    Делегирует работу специализированным компонентам:
    - OpenAIClient: HTTP + OpenAI API
    - ToolOrchestrator: function calling цикл
    """

    def __init__(
        self,
        config: Config,
        tools: list[Tool] | None = None,
    ) -> None:
        """
        Инициализация LLM клиента.

        Args:
            config: Конфигурация приложения
            tools: Список инструментов для function calling (опционально)
        """
        self.config = config
        self.tools = tools if tools is not None else self._get_default_tools()

        # Создаем компоненты (композиция)
        self.openai_client = OpenAIClient(config)
        self.orchestrator = ToolOrchestrator(
            self.openai_client,
            self.tools,
            config,
        )

        logger.info(
            f"LLMClient (фасад) инициализирован: модель={config.llm_model}, "
            f"tools={len(self.tools)}"
        )

    def _get_default_tools(self) -> list[Tool]:
        """
        Создает набор инструментов по умолчанию.

        Returns:
            Список стандартных инструментов
        """
        return [
            WikipediaTool(self.config),
            DateTimeTool(),
            WebSearchTool(self.config),
        ]

    async def get_response(self, messages: list[Message]) -> str | None:
        """
        Получить ответ от LLM с поддержкой function calling.

        Делегирует работу ToolOrchestrator.

        Args:
            messages: История сообщений

        Returns:
            Ответ от LLM или None при ошибке

        Examples:
            >>> client = LLMClient(config)
            >>> response = await client.get_response(messages)
        """
        return await self.orchestrator.process_with_tools(messages)
