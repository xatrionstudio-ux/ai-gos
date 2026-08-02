"""
Base AI Provider Adapter interface.

All LLM provider adapters (OpenAI, Anthropic, Gemini, Mistral, Local Llama) implement this port interface.
This ensures zero vendor lock-in and complete decoupling of AI providers from business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

from domains.ai.infrastructure.llm_router import LLMResponse

T = TypeVar("T", bound=BaseModel)


class BaseAIAdapter(ABC):
    """Abstract port interface for AI model provider adapters."""

    provider_name: str

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        response_format: type[T] | None = None,
    ) -> LLMResponse:
        """Execute completion call against provider API."""
        ...

    @abstractmethod
    def supports_model(self, model: str) -> bool:
        """Check if this adapter handles the target model name."""
        ...
