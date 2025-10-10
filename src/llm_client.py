"""Клиент для работы с OpenAI LLM."""

import json
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
            wikipedia_tool: Wikipedia tool для function calling
        """
        self.config = config
        self.wikipedia_tool = wikipedia_tool

        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
        )
        logger.info(f"LLMClient инициализирован с моделью {config.openai_model}")

    def _get_tools_schema(self) -> list[dict]:
        """
        Получить схему доступных инструментов для function calling.

        Returns:
            Список схем инструментов в формате OpenAI
        """
        if not self.wikipedia_tool:
            return []

        return [
            {
                "type": "function",
                "function": {
                    "name": "search_wikipedia",
                    "description": "Поиск информации в Wikipedia (русская и английская версии)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Поисковый запрос (название статьи или ключевые слова)",
                            },
                            "language": {
                                "type": "string",
                                "enum": ["ru", "en"],
                                "description": "Язык Wikipedia (ru - русский, en - английский)",
                                "default": "ru",
                            },
                        },
                        "required": ["query"],
                    },
                },
            }
        ]

    async def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """
        Выполнить вызов инструмента.

        Args:
            tool_name: Имя инструмента
            arguments: Аргументы для инструмента

        Returns:
            Результат выполнения инструмента
        """
        logger.info(f"Выполнение tool: {tool_name} с аргументами {arguments}")

        if tool_name == "search_wikipedia":
            query = arguments.get("query", "")
            language = arguments.get("language", "ru")
            result = await self.wikipedia_tool.search(query, language)
            return result

        logger.warning(f"Неизвестный tool: {tool_name}")
        return f"Ошибка: инструмент '{tool_name}' не найден"

    async def get_response(self, messages: list[Message]) -> str | None:
        """
        Получить ответ от LLM с поддержкой function calling.

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

            tools = self._get_tools_schema()

            # Цикл обработки tool calls (максимум 5 итераций)
            for iteration in range(5):
                logger.debug(
                    f"Запрос к LLM (итерация {iteration + 1}): {len(request_messages)} сообщений"
                )

                # Запрос к OpenAI API
                if tools:
                    response = await self.client.chat.completions.create(
                        model=self.config.openai_model,
                        messages=request_messages,
                        tools=tools,
                        temperature=0.7,
                        max_tokens=2000,
                    )
                else:
                    response = await self.client.chat.completions.create(
                        model=self.config.openai_model,
                        messages=request_messages,
                        temperature=0.7,
                        max_tokens=2000,
                    )

                assistant_message = response.choices[0].message

                # Если нет tool calls, возвращаем ответ
                if not assistant_message.tool_calls:
                    content = assistant_message.content
                    logger.info("Получен финальный ответ от LLM")
                    return content

                # Добавляем сообщение ассистента с tool calls
                # Формируем вручную, чтобы избежать лишних полей
                tool_calls_data = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_message.tool_calls
                ]

                request_messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": tool_calls_data,
                    }
                )

                # Выполняем tool calls
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

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
            logger.warning("Достигнут лимит итераций tool calls (5)")
            return "Извините, не удалось получить ответ (превышен лимит запросов)."

        except Exception as e:
            logger.error(f"Ошибка при обращении к LLM: {e}", exc_info=True)
            return None
