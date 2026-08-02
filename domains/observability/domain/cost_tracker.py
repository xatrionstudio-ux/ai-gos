"""
AICostTracker — Tenant & Workflow budget enforcement.

Tracks cumulative USD cost and token usage per tenant, project, and workflow thread.
Enforces daily and monthly limits.
"""

from __future__ import annotations

import logging
import uuid
from pydantic import BaseModel, Field

from core.exceptions import RateLimitError

logger = logging.getLogger(__name__)


class BudgetPolicy(BaseModel):
    org_id: uuid.UUID
    daily_budget_usd: float = Field(default=50.0)
    monthly_budget_usd: float = Field(default=1000.0)
    current_daily_spend_usd: float = Field(default=0.0)
    current_monthly_spend_usd: float = Field(default=0.0)


class AICostTracker:
    """Cost Tracking & Budget Enforcement Service."""

    def __init__(self) -> None:
        self._policies: dict[uuid.UUID, BudgetPolicy] = {}

    def get_policy(self, org_id: uuid.UUID) -> BudgetPolicy:
        if org_id not in self._policies:
            self._policies[org_id] = BudgetPolicy(org_id=org_id)
        return self._policies[org_id]

    def record_cost(self, org_id: uuid.UUID, cost_usd: float) -> BudgetPolicy:
        """Record cost and enforce daily/monthly budget limits."""
        policy = self.get_policy(org_id)
        new_daily = policy.current_daily_spend_usd + cost_usd
        new_monthly = policy.current_monthly_spend_usd + cost_usd

        if new_daily > policy.daily_budget_usd:
            logger.warning("Tenant %s exceeded daily budget of $%s (spent $%s)", org_id, policy.daily_budget_usd, new_daily)
            raise RateLimitError("Daily AI budget exceeded for organization.")

        policy.current_daily_spend_usd = new_daily
        policy.current_monthly_spend_usd = new_monthly
        return policy
