"""Инструмент для поиска актуальной информации в интернете."""

import logging
from typing import Any

from duckduckgo_search import DDGS

from src.config import Config

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Инструмент для поиска актуальной информации через DuckDuckGo."""

    def __init__(self, config: Config) -> None:
        """
        Инициализация WebSearchTool.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.ddgs = DDGS()
        logger.info("WebSearchTool инициализирован")

    def get_schema(self) -> dict[str, Any]:
        """
        Возвращает JSON схему для OpenAI function calling.

        Returns:
            Схема функции в формате OpenAI
        """
        return {
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
                            "description": f"Максимальное количество результатов (1-{self.config.websearch_max_results})",
                            "default": self.config.websearch_default_results,
                            "minimum": 1,
                            "maximum": self.config.websearch_max_results,
                        },
                    },
                    "required": ["query"],
                },
            },
        }

    async def execute(self, **kwargs: Any) -> str:
        """
        Выполняет инструмент с переданными аргументами.

        Args:
            **kwargs: query, max_results

        Returns:
            Результаты поиска
        """
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results")
        return await self.search(query, max_results)

    async def search(self, query: str, max_results: int | None = None) -> str:
        """
        Поиск актуальной информации в интернете.

        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов (опционально)

        Returns:
            Структурированные результаты поиска с заголовками, описаниями и ссылками

        Examples:
            >>> tool = WebSearchTool(config)
            >>> result = await tool.search("президент Зимбабве 2025", max_results=2)
        """
        try:
            # Используем дефолтное значение из config если не передано
            if max_results is None:
                max_results = self.config.websearch_default_results

            # Ограничиваем количество результатов
            max_results = max(1, min(max_results, self.config.websearch_max_results))

            logger.info(f"Поиск в DuckDuckGo: '{query}' (max_results={max_results})")

            # Выполняем поиск
            results = []
            sources = []
            try:
                search_results = self.ddgs.text(query, max_results=max_results)

                for idx, result in enumerate(search_results, 1):
                    title = result.get("title", "Без названия")
                    body = result.get("body", "")
                    href = result.get("href", "")

                    # Формируем результат с кликабельной ссылкой
                    results.append(f"{idx}. **{title}**")
                    if body:
                        # Обрезаем описание если слишком длинное
                        max_length = self.config.websearch_max_body_length
                        if len(body) > max_length:
                            body = body[: max_length - 3] + "..."
                        results.append(f"   {body}")
                    if href:
                        results.append(f"   🔗 {href}")
                        sources.append(f"📚 [{title}]({href})")
                    results.append("")  # Пустая строка для разделения

            except Exception as search_error:
                logger.error(f"Ошибка при выполнении поиска: {search_error}")
                return f"Ошибка при поиске: {search_error}"

            if not results:
                logger.warning(f"Результатов не найдено для запроса: {query}")
                return f"По запросу '{query}' результатов не найдено."

            formatted_results = "\n".join(results)

            # Добавляем источники в конце для удобства цитирования
            if sources:
                formatted_results += "\n📚 **Источники:**\n" + "\n".join(sources)

            logger.info(f"Найдено {len(sources)} результатов")

            return f"Результаты поиска по запросу '{query}':\n\n{formatted_results}"

        except Exception as e:
            logger.error(f"Ошибка в WebSearchTool: {e}", exc_info=True)
            return f"Ошибка при поиске информации: {e}"
