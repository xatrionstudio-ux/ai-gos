"""
BaseAgent abstract class — foundation for all 26 specialized AI agents.

Guarantees:
- Every agent execution is observable (OTEL span + DB call log)
- Every response includes a confidence score (0.0 to 1.0)
- Every prompt is loaded from PromptRegistry by version
- Standard retries with exponential backoff
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from core.exceptions import AIProviderError

logger = logging.getLogger(__name__)

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class AgentOutput(BaseModel, Generic[TOutput]):
    """Standardized output wrapper for all agents."""

    result: TOutput
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score of the AI output")
    agent_name: str
    prompt_version: str
    model_used: str
    execution_time_ms: int
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    trace_id: str | None = None


class BaseAgent(ABC, Generic[TInput, TOutput]):
    """
    Abstract Base Class for all AI agents.

    Implementations must define:
    - name: str
    - prompt_name: str
    - input_schema: type[TInput]
    - output_schema: type[TOutput]
    - _run_internal(input_data, prompt_template) -> (TOutput, confidence, token_counts)
    """

    name: str
    prompt_name: str
    default_model: str = "gpt-4o"
    max_retries: int = 3

    def __init__(self, llm_router: Any = None, call_logger: Any = None) -> None:
        self._llm = llm_router
        self._logger = call_logger

    @abstractmethod
    async def process(
        self,
        input_data: TInput,
        workflow_id: uuid.UUID | None = None,
        prompt_version: str = "latest",
        trace_id: str | None = None,
    ) -> AgentOutput[TOutput]:
        """Execute the agent with observability, retries, and confidence scoring."""
        ...

    @staticmethod
    def compute_request_hash(prompt: str, input_data: BaseModel) -> str:
        """Compute SHA-256 hash of input for reproducibility auditing."""
        payload = f"{prompt}:{input_data.model_dump_json()}"
        return hashlib.sha256(payload.encode()).hexdigest()
