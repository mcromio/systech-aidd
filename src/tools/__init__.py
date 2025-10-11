"""Инструменты для LLM с function calling."""

from src.tools.base import Tool
from src.tools.datetime import DateTimeTool
from src.tools.websearch import WebSearchTool
from src.tools.wikipedia import WikipediaTool

__all__ = [
    "Tool",
    "DateTimeTool",
    "WebSearchTool",
    "WikipediaTool",
]
