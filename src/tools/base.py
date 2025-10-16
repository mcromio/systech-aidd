"""Базовый протокол для инструментов LLM."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """
    Базовый протокол для всех инструментов LLM.

    Все инструменты должны реализовывать этот интерфейс для
    совместимости с LLMClient и единообразия API.
    """

    def get_schema(self) -> dict[str, Any]:
        """
        Возвращает JSON схему для OpenAI function calling.

        Returns:
            Схема функции в формате OpenAI:
            {
                "type": "function",
                "function": {
                    "name": "tool_name",
                    "description": "...",
                    "parameters": {...}
                }
            }
        """
        ...

    async def execute(self, **kwargs: Any) -> str:
        """
        Выполняет инструмент с переданными аргументами.

        Args:
            **kwargs: Аргументы для выполнения инструмента

        Returns:
            Результат выполнения в виде строки
        """
        ...
