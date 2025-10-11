"""Инструмент для поиска информации в Wikipedia."""

import logging
from typing import Any

import wikipediaapi

from src.config import Config

logger = logging.getLogger(__name__)


class WikipediaTool:
    """Инструмент для поиска в Wikipedia."""

    def __init__(self, config: Config) -> None:
        """
        Инициализация Wikipedia клиента.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        user_agent = config.wikipedia_user_agent

        self.wiki_ru = wikipediaapi.Wikipedia(
            language="ru",
            user_agent=user_agent,
        )
        self.wiki_en = wikipediaapi.Wikipedia(
            language="en",
            user_agent=user_agent,
        )
        logger.info("WikipediaTool инициализирован")

    def get_schema(self) -> dict[str, Any]:
        """
        Возвращает JSON схему для OpenAI function calling.

        Returns:
            Схема функции в формате OpenAI
        """
        return {
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

    async def execute(self, **kwargs: Any) -> str:
        """
        Выполняет инструмент с переданными аргументами.

        Args:
            **kwargs: query, language

        Returns:
            Результат поиска в Wikipedia
        """
        query = kwargs.get("query", "")
        language = kwargs.get("language", "ru")
        return await self.search(query, language)

    async def search(self, query: str, language: str = "ru") -> str:
        """
        Поиск статьи в Wikipedia.

        Args:
            query: Поисковый запрос
            language: Язык Wikipedia (ru/en)

        Returns:
            Краткое содержание статьи или сообщение об ошибке
        """
        logger.info(f"Поиск в Wikipedia: '{query}' ({language})")

        try:
            wiki = self.wiki_ru if language == "ru" else self.wiki_en
            page = wiki.page(query)

            if not page.exists():
                logger.warning(f"Статья не найдена: {query}")
                return f"Статья '{query}' не найдена в Wikipedia ({language})."

            # Возвращаем summary (первый абзац)
            max_length = self.config.wikipedia_max_summary_length
            summary = page.summary[:max_length]

            if len(page.summary) > max_length:
                summary += "..."

            result = f"{summary}\n\nИсточник: {page.fullurl}"
            logger.info(f"Найдена статья: {page.title}")
            return result

        except Exception as e:
            logger.error(f"Ошибка поиска в Wikipedia: {e}")
            return f"Ошибка при поиске в Wikipedia: {str(e)}"
