"""
BillingMeteringEngine — Consumption-based billing meter for multi-tenant SaaS.

Rule from 12 Specification:
- Billing is metered by consumption, not fixed seats.
- Meters: tokens, model rates, tool calls, vector storage, and workflow CPU/GPU time.
"""

from __future__ import annotations

import logging
import uuid
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class UsageRecord(BaseModel):
    org_id: uuid.UUID
    project_id: uuid.UUID
    workflow_id: uuid.UUID | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model_name: str = "gpt-4o"
    tool_api_calls: int = 0
    vector_storage_bytes: int = 0
    cpu_ms: int = 0


MODEL_RATES = {
    "gpt-4o": {"prompt_per_1k": 0.0025, "completion_per_1k": 0.010},
    "claude-3-5-sonnet": {"prompt_per_1k": 0.0030, "completion_per_1k": 0.015},
    "gemini-1.5-pro": {"prompt_per_1k": 0.00125, "completion_per_1k": 0.005},
    "gpt-4o-mini": {"prompt_per_1k": 0.00015, "completion_per_1k": 0.0006},
}


class BillingMeteringEngine:
    """Calculates exact usage cost per execution."""

    @staticmethod
    def calculate_usage_cost(record: UsageRecord) -> float:
        """Calculate total USD cost for a usage record."""
        rates = MODEL_RATES.get(record.model_name, MODEL_RATES["gpt-4o"])
        token_cost = (record.prompt_tokens / 1000.0) * rates["prompt_per_1k"] + (record.completion_tokens / 1000.0) * rates["completion_per_1k"]
        tool_cost = record.tool_api_calls * 0.001  # Average $0.001 per tool API execution
        cpu_cost = (record.cpu_ms / 1000.0) * 0.00001  # Micro-charge for CPU execution

        total_cost = token_cost + tool_cost + cpu_cost
        logger.debug("Metered usage cost for org %s: $%0.6f", record.org_id, total_cost)
        return total_cost
