"""OpenAI API клиент."""

import logging
from typing import Any

import httpx
from openai import AsyncOpenAI

from src.config import Config

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Чистый wrapper над OpenAI API.

    Отвечает только за:
    - Конфигурацию HTTP клиента (proxy, timeout)
    - Вызовы OpenAI API
    """

    def __init__(self, config: Config) -> None:
        """
        Инициализация OpenAI клиента.

        Args:
            config: Конфигурация приложения
        """
        self.config = config

        # Создаем HTTP клиент с headers для OpenRouter
        default_headers = {}
        if "openrouter.ai" in config.llm_base_url:
            default_headers = {
                "HTTP-Referer": "https://github.com/systech-aidd",
                "X-Title": "SYSTECH LLM Assistant",
            }
        
        http_client = httpx.AsyncClient(
            timeout=config.llm_timeout,
            headers=default_headers,
        )

        self.client = AsyncOpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            http_client=http_client,
        )

        logger.info(
            f"OpenAIClient инициализирован: модель={config.llm_model}, "
            f"base_url={config.llm_base_url}"
        )

    async def create_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        """
        Создать completion с OpenAI API.

        Args:
            messages: Список сообщений для LLM
            tools: Опциональный список tools для function calling

        Returns:
            Ответ от OpenAI API

        Examples:
            >>> client = OpenAIClient(config)
            >>> response = await client.create_completion(
            ...     messages=[{"role": "user", "content": "Hello"}]
            ... )
        """
        # Выбираем max_tokens в зависимости от наличия tools
        max_tokens = (
            self.config.llm_max_tokens_with_tools if tools else self.config.llm_max_tokens_no_tools
        )

        logger.debug(
            f"create_completion: model={self.config.llm_model}, "
            f"messages={len(messages)}, tools={len(tools) if tools else 0}, "
            f"max_tokens={max_tokens}"
        )

        # Вызываем LLM API (с tools или без)
        if tools:
            return await self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,  # type: ignore[arg-type]
                tools=tools,  # type: ignore[arg-type]
                max_completion_tokens=max_tokens,
            )
        else:
            return await self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,  # type: ignore[arg-type]
                max_completion_tokens=max_tokens,
            )
