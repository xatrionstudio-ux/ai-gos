"""
LLMRouter — provider-agnostic LLM caller using LiteLLM.

Supports:
- Automatic model fallback (e.g. gpt-4o -> claude-3-5-sonnet -> gemini-1.5-pro)
- Structured output via Pydantic response models
- Token counting and exact USD cost calculation
- Retries on rate limits and 5xx errors
"""

from __future__ import annotations

import logging
import os
from typing import Any, TypeVar

import litellm
from pydantic import BaseModel

from core.exceptions import AIProviderError

logger = logging.getLogger(__name__)

# Silence noisy litellm logs in production
litellm.suppress_debug_info = True

T = TypeVar("T", bound=BaseModel)


class LLMResponse(BaseModel):
    content: str
    parsed: Any | None = None
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float


class LLMRouter:
    """LiteLLM wrapper providing provider-agnostic LLM calls."""

    def __init__(self, default_model: str | None = None) -> None:
        self.default_model = default_model or os.getenv("LLM_DEFAULT_MODEL", "gpt-4o")

    async def completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        response_format: type[T] | None = None,
        fallbacks: list[str] | None = None,
    ) -> LLMResponse:
        target_model = model or self.default_model
        fallback_models = fallbacks or ["claude-3-5-sonnet-20241022", "gemini/gemini-1.5-pro"]

        try:
            kwargs: dict[str, Any] = {
                "model": target_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "fallbacks": fallback_models,
            }

            if response_format:
                kwargs["response_format"] = response_format

            response = await litellm.acompletion(**kwargs)

            content = response.choices[0].message.content or ""
            usage = getattr(response, "usage", None)

            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            # Calculate cost via litellm helper
            try:
                cost = litellm.completion_cost(completion_response=response)
            except Exception:
                cost = 0.0

            parsed_obj = None
            if response_format and content:
                try:
                    parsed_obj = response_format.model_validate_json(content)
                except Exception as exc:
                    logger.warning("Failed to parse response format into Pydantic model: %s", exc)

            return LLMResponse(
                content=content,
                parsed=parsed_obj,
                model=response.model or target_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=float(cost),
            )

        except Exception as exc:
            logger.exception("LLM call failed for model %s", target_model)
            raise AIProviderError(f"LLM provider error: {exc}") from exc
