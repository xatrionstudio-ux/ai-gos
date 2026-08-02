"""
FeatureFlagService — Feature Flag & Plan Tier Policy Engine.

Enforces subscription tier capabilities:
- Starter: 1 Project, 5 Agents, 100 daily workflows
- Professional: 20 Projects, Unlimited Agents, Full PKL, Marketplace
- Business: Multi-Workspace, SSO, SLAs, Audit Trail
- Enterprise: Dedicated VPC, BYOK, On-Prem, HIPAA
"""

from __future__ import annotations

import uuid
from enum import Enum

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        pass

from pydantic import BaseModel, Field


class PlanTier(StrEnum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class PlanLimits(BaseModel):
    max_projects: int
    max_agents: int
    max_daily_workflows: int
    allowed_models: list[str]
    sso_enabled: bool
    byok_enabled: bool
    dedicated_vpc: bool


PLAN_PRESETS: dict[PlanTier, PlanLimits] = {
    PlanTier.STARTER: PlanLimits(
        max_projects=1,
        max_agents=5,
        max_daily_workflows=100,
        allowed_models=["gpt-4o-mini", "claude-3-5-haiku"],
        sso_enabled=False,
        byok_enabled=False,
        dedicated_vpc=False,
    ),
    PlanTier.PROFESSIONAL: PlanLimits(
        max_projects=20,
        max_agents=999,
        max_daily_workflows=5000,
        allowed_models=["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"],
        sso_enabled=False,
        byok_enabled=False,
        dedicated_vpc=False,
    ),
    PlanTier.BUSINESS: PlanLimits(
        max_projects=100,
        max_agents=9999,
        max_daily_workflows=50000,
        allowed_models=["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro", "o1-preview"],
        sso_enabled=True,
        byok_enabled=False,
        dedicated_vpc=False,
    ),
    PlanTier.ENTERPRISE: PlanLimits(
        max_projects=99999,
        max_agents=99999,
        max_daily_workflows=999999,
        allowed_models=["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro", "o1-preview", "local-llama"],
        sso_enabled=True,
        byok_enabled=True,
        dedicated_vpc=True,
    ),
}


class FeatureFlagService:
    """Evaluates plan tier permissions and tenant feature flags."""

    @staticmethod
    def get_plan_limits(plan_tier: PlanTier) -> PlanLimits:
        return PLAN_PRESETS.get(plan_tier, PLAN_PRESETS[PlanTier.STARTER])

    @staticmethod
    def is_model_allowed(plan_tier: PlanTier, model_name: str) -> bool:
        limits = FeatureFlagService.get_plan_limits(plan_tier)
        return model_name in limits.allowed_models or plan_tier == PlanTier.ENTERPRISE
