"""Оркестратор для управления function calling циклом."""

import json
import logging
from typing import Any

from src.config import Config
from src.context_manager import Message
from src.llm.client import OpenAIClient
from src.tools import Tool

logger = logging.getLogger(__name__)


class ToolOrchestrator:
    """
    Управление циклом function calling.

    Отвечает за:
    - Цикл обработки tool calls (до N итераций)
    - Логику ограничений (websearch_count)
    - Выполнение инструментов через Tool.execute()
    - Формирование запросов к LLM
    """

    def __init__(
        self,
        openai_client: OpenAIClient,
        tools: list[Tool],
        config: Config,
    ) -> None:
        """
        Инициализация оркестратора.

        Args:
            openai_client: Клиент для OpenAI API
            tools: Список доступных инструментов
            config: Конфигурация приложения
        """
        self.openai_client = openai_client
        self.tools = tools
        self.config = config

        logger.info(f"ToolOrchestrator инициализирован с {len(tools)} инструментами")

    def _get_tools_schema(self) -> list[dict[str, Any]]:
        """
        Получить схему доступных инструментов для function calling.

        Returns:
            Список схем инструментов в формате OpenAI
        """
        return [tool.get_schema() for tool in self.tools]

    async def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """
        Выполнить вызов инструмента.

        Args:
            tool_name: Имя инструмента
            arguments: Аргументы для инструмента

        Returns:
            Результат выполнения инструмента
        """
        logger.info(f"Выполнение tool: {tool_name} с аргументами {arguments}")

        # Ищем инструмент по имени в схеме
        for tool in self.tools:
            schema = tool.get_schema()
            if schema["function"]["name"] == tool_name:
                result = await tool.execute(**arguments)
                return str(result)

        logger.warning(f"Неизвестный tool: {tool_name}")
        return f"Ошибка: инструмент '{tool_name}' не найден"

    async def process_with_tools(self, messages: list[Message]) -> str | None:
        """
        Обработать запрос с поддержкой function calling.

        Args:
            messages: История сообщений

        Returns:
            Ответ от LLM или None при ошибке

        Examples:
            >>> orchestrator = ToolOrchestrator(openai_client, tools, config)
            >>> response = await orchestrator.process_with_tools(messages)
        """
        try:
            # Формируем запрос с системным промптом
            request_messages: list[dict[str, Any]] = [
                {"role": "system", "content": self.config.system_prompt}
            ]

            # Добавляем историю диалога
            for msg in messages:
                request_messages.append({"role": msg.role, "content": msg.content})

            tools_schema = self._get_tools_schema()

            # Счетчик веб-запросов (максимум N)
            websearch_count = 0
            max_websearch = self.config.llm_max_websearch_calls

            # Цикл обработки tool calls
            for iteration in range(self.config.llm_max_tool_iterations):
                logger.debug(
                    f"Запрос к LLM (итерация {iteration + 1}): {len(request_messages)} сообщений"
                )

                # Запрос к OpenAI API
                response = await self.openai_client.create_completion(
                    messages=request_messages,
                    tools=tools_schema if tools_schema else None,
                )

                assistant_message = response.choices[0].message

                # Если нет tool calls, возвращаем ответ
                if not assistant_message.tool_calls:
                    content = assistant_message.content
                    logger.info("Получен финальный ответ от LLM")
                    return str(content) if content else None

                # Добавляем сообщение ассистента с tool calls
                # Формируем вручную, чтобы избежать лишних полей
                tool_calls_data = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,  # type: ignore[union-attr]
                            "arguments": tc.function.arguments,  # type: ignore[union-attr]
                        },
                    }
                    for tc in assistant_message.tool_calls
                ]

                request_messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content,  # type: ignore[dict-item]
                        "tool_calls": tool_calls_data,  # type: ignore[dict-item]
                    }
                )

                # Выполняем tool calls
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name  # type: ignore[union-attr]
                    arguments = json.loads(tool_call.function.arguments)  # type: ignore[union-attr]

                    # Проверяем лимит веб-запросов
                    if tool_name == "web_search":
                        if websearch_count >= max_websearch:
                            logger.warning(
                                f"Достигнут лимит веб-запросов ({max_websearch}). Пропускаем вызов."
                            )
                            tool_result = (
                                f"⚠️ Достигнут лимит веб-запросов ({max_websearch}). "
                                "Используй уже полученную информацию для ответа."
                            )
                        else:
                            websearch_count += 1
                            logger.info(
                                f"Вызов tool: {tool_name} (веб-запрос {websearch_count}/{max_websearch})"
                            )
                            tool_result = await self._execute_tool(tool_name, arguments)
                    else:
                        logger.info(f"Вызов tool: {tool_name}")
                        tool_result = await self._execute_tool(tool_name, arguments)

                    # Добавляем результат tool call
                    request_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result,
                        }
                    )

            # Если достигли лимита итераций
            logger.warning(
                f"Достигнут лимит итераций tool calls ({self.config.llm_max_tool_iterations})"
            )
            return "Извините, не удалось получить ответ (превышен лимит запросов). Попробуйте задать более конкретный вопрос."

        except Exception as e:
            logger.error(f"Ошибка при обработке с tools: {e}", exc_info=True)
            return None

