"""
Unit tests for Specification 12: Multi-Tenant Control Plane, Feature Flags, Billing Metering, and ABAC Engine.
"""

import pytest
import uuid

from core.exceptions import AuthorizationError
from domains.identity.domain.abac_engine import ABACEngine, AccessContext
from domains.identity.domain.entities.user import Permission, User
from domains.tenant.domain.billing_metering import BillingMeteringEngine, UsageRecord
from domains.tenant.domain.feature_flags import FeatureFlagService, PlanTier


def test_feature_flags_and_plan_limits():
    starter_limits = FeatureFlagService.get_plan_limits(PlanTier.STARTER)
    assert starter_limits.max_projects == 1
    assert starter_limits.sso_enabled is False

    ent_limits = FeatureFlagService.get_plan_limits(PlanTier.ENTERPRISE)
    assert ent_limits.sso_enabled is True
    assert ent_limits.byok_enabled is True

    assert FeatureFlagService.is_model_allowed(PlanTier.STARTER, "gpt-4o-mini") is True
    assert FeatureFlagService.is_model_allowed(PlanTier.STARTER, "o1-preview") is False


def test_billing_metering_calculation():
    record = UsageRecord(
        org_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        prompt_tokens=1000,      # $0.0025
        completion_tokens=500,   # $0.0050
        model_name="gpt-4o",
        tool_api_calls=2,        # $0.0020
        cpu_ms=100,              # $0.000001
    )
    cost = BillingMeteringEngine.calculate_usage_cost(record)
    assert cost > 0.009
    assert cost < 0.010


def test_abac_security_engine():
    org_id = uuid.uuid4()
    user = User(
        org_id=org_id,
        email="marketing@test.com",
        hashed_password="hash",
        is_superuser=True,
    )

    ctx_ok = AccessContext(user_department="Marketing", tenant_plan="professional")
    assert ABACEngine.authorize(user, Permission.CONTENT_PUBLISH, ctx_ok) is True

    ctx_fail = AccessContext(user_department="Engineering", tenant_plan="starter")
    with pytest.raises(AuthorizationError):
        ABACEngine.authorize(user, Permission.CONTENT_PUBLISH, ctx_fail)
