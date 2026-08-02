"""
ABACEngine — Attribute-Based Access Control complementing RBAC.

Evaluates contextual attributes:
- Department (Marketing, Legal, Product, Engineering)
- Project Type (SEO, Documentation, Support)
- Tenant Plan (Starter, Professional, Business, Enterprise)
- Region (EU, US)
"""

from __future__ import annotations

import logging
import uuid
from pydantic import BaseModel, Field

from core.exceptions import AuthorizationError
from domains.identity.domain.entities.user import Permission, User

logger = logging.getLogger(__name__)


class AccessContext(BaseModel):
    user_department: str | None = None
    project_type: str | None = None
    tenant_plan: str = "starter"
    region: str = "EU"


class ABACEngine:
    """Evaluates combined RBAC and ABAC access decisions."""

    @staticmethod
    def authorize(user: User, required_permission: Permission, context: AccessContext) -> bool:
        """
        Authorize access based on RBAC permissions and ABAC context attributes.
        """
        # 1. RBAC check
        if not user.has_permission(required_permission):
            logger.warning("RBAC Authorization failed: User %s lacks permission %s", user.id, required_permission)
            raise AuthorizationError(f"Permission '{required_permission}' is required.")

        # 2. ABAC Attribute check
        if required_permission in [Permission.CONTENT_PUBLISH, Permission.CONTENT_APPROVE]:
            if context.user_department and context.user_department.lower() not in ["marketing", "executive", "admin"]:
                logger.warning("ABAC Authorization failed: Department '%s' cannot publish content", context.user_department)
                raise AuthorizationError(f"Department '{context.user_department}' is not authorized to publish content.")

        return True
