"""Клиент для работы с OpenAI LLM."""

import json
import logging

import httpx
from openai import AsyncOpenAI

from src.config import Config
from src.context_manager import Message
from src.datetime_tool import DateTimeTool
from src.websearch_tool import WebSearchTool

logger = logging.getLogger(__name__)


class LLMClient:
    """Клиент для работы с OpenAI API."""

    def __init__(
        self,
        config: Config,
        wikipedia_tool=None,
        datetime_tool=None,
        websearch_tool=None,
    ):
        """
        Инициализация LLM клиента.

        Args:
            config: Конфигурация приложения
            wikipedia_tool: Wikipedia tool для function calling
            datetime_tool: DateTimeTool для получения текущей даты/времени
            websearch_tool: WebSearchTool для поиска актуальной информации
        """
        self.config = config
        self.wikipedia_tool = wikipedia_tool
        self.datetime_tool = datetime_tool or DateTimeTool()
        self.websearch_tool = websearch_tool or WebSearchTool()

        # Создаем HTTP клиент с прокси
        http_client = httpx.AsyncClient(
            proxy=config.openai_proxy_url,
            timeout=config.openai_timeout,
        )

        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            http_client=http_client,
        )
        logger.info(
            f"LLMClient инициализирован с моделью {config.openai_model} "
            f"через прокси {config.openai_proxy_url}"
        )

    def _get_tools_schema(self) -> list[dict]:
        """
        Получить схему доступных инструментов для function calling.

        Returns:
            Список схем инструментов в формате OpenAI
        """
        tools = []

        # Wikipedia search
        if self.wikipedia_tool:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "search_wikipedia",
                        "description": "Поиск информации в Wikipedia (русская и английская версии). Используй для статичной энциклопедической информации.",
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
            )

        # Current date/time
        if self.datetime_tool:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "get_current_datetime",
                        "description": "Получить текущую дату и время. Используй когда пользователь спрашивает 'какая сегодня дата', 'сколько времени', 'какой сейчас день недели' и т.п.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "timezone": {
                                    "type": "string",
                                    "description": "Часовой пояс (UTC, Europe/Moscow, America/New_York, Asia/Tokyo, etc.)",
                                    "default": "UTC",
                                },
                                "format_type": {
                                    "type": "string",
                                    "enum": ["full", "date", "time"],
                                    "description": "Формат: full (дата+время), date (только дата), time (только время)",
                                    "default": "full",
                                },
                            },
                            "required": [],
                        },
                    },
                }
            )

        # Web search for current information
        if self.websearch_tool:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Поиск АКТУАЛЬНОЙ информации в интернете через DuckDuckGo. Используй для вопросов о текущих событиях, политиках, новостях, ценах, погоде и т.д. НЕ используй для общеизвестных фактов из Wikipedia.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Поисковый запрос (на русском или английском)",
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Максимальное количество результатов (1-5)",
                                    "default": 3,
                                    "minimum": 1,
                                    "maximum": 5,
                                },
                            },
                            "required": ["query"],
                        },
                    },
                }
            )

        return tools

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

        elif tool_name == "get_current_datetime":
            timezone = arguments.get("timezone", "UTC")
            format_type = arguments.get("format_type", "full")
            result = self.datetime_tool.get_current_datetime(timezone, format_type)
            return result

        elif tool_name == "web_search":
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 3)
            result = await self.websearch_tool.search(query, max_results)
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

            # Счетчик веб-запросов (максимум 2)
            websearch_count = 0
            max_websearch = 2

            # Цикл обработки tool calls (максимум 10 итераций)
            for iteration in range(10):
                logger.debug(
                    f"Запрос к LLM (итерация {iteration + 1}): {len(request_messages)} сообщений"
                )

                # Запрос к OpenAI API
                # Для некоторых моделей (gpt-5) temperature не настраивается - используем дефолт
                if tools:
                    response = await self.client.chat.completions.create(
                        model=self.config.openai_model,
                        messages=request_messages,
                        tools=tools,
                        max_completion_tokens=10000,
                    )
                else:
                    response = await self.client.chat.completions.create(
                        model=self.config.openai_model,
                        messages=request_messages,
                        max_completion_tokens=12000,
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
            logger.warning("Достигнут лимит итераций tool calls (10)")
            return "Извините, не удалось получить ответ (превышен лимит запросов). Попробуйте задать более конкретный вопрос."

        except Exception as e:
            logger.error(f"Ошибка при обращении к LLM: {e}", exc_info=True)
            return None
