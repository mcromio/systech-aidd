"""Инструмент для поиска актуальной информации в интернете."""

import logging

from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Инструмент для поиска актуальной информации через DuckDuckGo."""

    def __init__(self) -> None:
        """Инициализация WebSearchTool."""
        self.ddgs = DDGS()
        logger.info("WebSearchTool инициализирован")

    async def search(self, query: str, max_results: int = 3) -> str:
        """
        Поиск актуальной информации в интернете.

        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов (1-5)

        Returns:
            Структурированные результаты поиска с заголовками, описаниями и ссылками

        Examples:
            >>> tool = WebSearchTool()
            >>> result = await tool.search("президент Зимбабве 2025", max_results=2)
        """
        try:
            # Ограничиваем количество результатов
            max_results = max(1, min(max_results, 5))

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
                        if len(body) > 200:
                            body = body[:197] + "..."
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
