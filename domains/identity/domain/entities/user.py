"""
Identity Domain — User and Organization entities.

These are the core aggregates of the Identity bounded context.
All authentication state lives here. Business rules are enforced
by entity methods — never by infrastructure code.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

UTC = timezone.utc
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import EmailStr, Field

from core.base_entity import AggregateRoot, BaseEntity
from core.exceptions import AuthorizationError, ValidationError

if TYPE_CHECKING:
    pass


class Permission(StrEnum):
    """Granular permissions for RBAC."""

    # Projects
    PROJECTS_READ = "projects:read"
    PROJECTS_WRITE = "projects:write"
    PROJECTS_DELETE = "projects:delete"

    # Knowledge
    KNOWLEDGE_READ = "knowledge:read"
    KNOWLEDGE_WRITE = "knowledge:write"

    # Content
    CONTENT_READ = "content:read"
    CONTENT_WRITE = "content:write"
    CONTENT_PUBLISH = "content:publish"
    CONTENT_APPROVE = "content:approve"

    # SEO
    SEO_READ = "seo:read"
    SEO_WRITE = "seo:write"

    # Analytics
    ANALYTICS_READ = "analytics:read"

    # Workflows
    WORKFLOWS_READ = "workflows:read"
    WORKFLOWS_WRITE = "workflows:write"
    WORKFLOWS_MANAGE = "workflows:manage"

    # AI / Prompts
    AI_READ = "ai:read"
    AI_MANAGE = "ai:manage"

    # Admin
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"

    # Billing
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"

    # Members
    MEMBERS_READ = "members:read"
    MEMBERS_WRITE = "members:write"


# Predefined role permission sets
ROLE_PERMISSIONS: dict[str, list[Permission]] = {
    "owner": list(Permission),  # All permissions
    "admin": [
        Permission.PROJECTS_READ, Permission.PROJECTS_WRITE,
        Permission.KNOWLEDGE_READ, Permission.KNOWLEDGE_WRITE,
        Permission.CONTENT_READ, Permission.CONTENT_WRITE,
        Permission.CONTENT_PUBLISH, Permission.CONTENT_APPROVE,
        Permission.SEO_READ, Permission.SEO_WRITE,
        Permission.ANALYTICS_READ,
        Permission.WORKFLOWS_READ, Permission.WORKFLOWS_WRITE, Permission.WORKFLOWS_MANAGE,
        Permission.AI_READ, Permission.AI_MANAGE,
        Permission.MEMBERS_READ, Permission.MEMBERS_WRITE,
        Permission.BILLING_READ,
    ],
    "editor": [
        Permission.PROJECTS_READ,
        Permission.KNOWLEDGE_READ,
        Permission.CONTENT_READ, Permission.CONTENT_WRITE,
        Permission.CONTENT_APPROVE,
        Permission.SEO_READ,
        Permission.ANALYTICS_READ,
        Permission.WORKFLOWS_READ, Permission.WORKFLOWS_WRITE,
        Permission.AI_READ,
    ],
    "viewer": [
        Permission.PROJECTS_READ,
        Permission.KNOWLEDGE_READ,
        Permission.CONTENT_READ,
        Permission.SEO_READ,
        Permission.ANALYTICS_READ,
        Permission.WORKFLOWS_READ,
    ],
}


class Organization(AggregateRoot):
    """
    Organization aggregate root.

    An organization represents one tenant. All data within the system
    is scoped to an organization. Deleting an organization cascades to
    all resources via ON DELETE CASCADE in PostgreSQL.
    """

    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$")
    plan: str = Field(default="starter")
    settings: dict = Field(default_factory=dict)
    is_active: bool = Field(default=True)

    def deactivate(self) -> "Organization":
        if not self.is_active:
            raise ValidationError("Organization is already inactive.")
        return self.model_copy(update={"is_active": False, "updated_at": datetime.now(UTC)})

    def update_settings(self, **kwargs) -> "Organization":
        new_settings = {**self.settings, **kwargs}
        return self.model_copy(update={"settings": new_settings, "updated_at": datetime.now(UTC)})


class Role(BaseEntity):
    """Role within an organization — maps to a set of Permissions."""

    org_id: uuid.UUID
    name: str = Field(min_length=2, max_length=50)
    permissions: list[Permission] = Field(default_factory=list)

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

    @classmethod
    def from_preset(cls, org_id: uuid.UUID, role_name: str) -> "Role":
        """Create a role from a preset definition."""
        if role_name not in ROLE_PERMISSIONS:
            raise ValidationError(f"Unknown role preset: {role_name}")
        return cls(
            org_id=org_id,
            name=role_name,
            permissions=ROLE_PERMISSIONS[role_name],
        )


class User(AggregateRoot):
    """
    User aggregate.

    Password is stored as a hashed value only. The raw password
    never leaves the authentication service. Argon2id is used via
    the PasswordHasher infrastructure service.
    """

    org_id: uuid.UUID
    email: EmailStr
    email_verified: bool = Field(default=False)
    hashed_password: str  # Argon2id hash — NEVER store plaintext
    full_name: str | None = None
    avatar_url: str | None = None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    last_login: datetime | None = None
    role_ids: list[uuid.UUID] = Field(default_factory=list)

    # In-memory resolved permissions (populated by application service)
    _resolved_permissions: list[Permission] = []

    def verify_is_active(self) -> None:
        """Raise if user account is disabled."""
        if not self.is_active:
            raise AuthorizationError("This account has been deactivated.")

    def record_login(self) -> "User":
        """Return updated user with last_login timestamp."""
        return self.model_copy(update={"last_login": datetime.now(UTC)})

    def verify_email(self) -> "User":
        return self.model_copy(update={"email_verified": True, "updated_at": datetime.now(UTC)})

    def update_password(self, new_hashed: str) -> "User":
        return self.model_copy(
            update={"hashed_password": new_hashed, "updated_at": datetime.now(UTC)}
        )

    def deactivate(self) -> "User":
        return self.model_copy(update={"is_active": False, "updated_at": datetime.now(UTC)})

    def has_permission(self, permission: Permission) -> bool:
        if self.is_superuser:
            return True
        return permission in self._resolved_permissions

    def require_permission(self, permission: Permission) -> None:
        """Raise AuthorizationError if user lacks the given permission."""
        if not self.has_permission(permission):
            raise AuthorizationError(
                f"Permission '{permission}' is required for this action."
            )


class RefreshToken(BaseEntity):
    """
    Refresh token entity.

    Stored in the database — allows revocation on logout and
    invalidation on password change or deactivation.
    Tokens are stored as their SHA-256 hash, not plaintext.
    """

    user_id: uuid.UUID
    org_id: uuid.UUID
    token_hash: str  # SHA-256 of the raw token — NEVER store the raw token
    expires_at: datetime
    revoked_at: datetime | None = None
    user_agent: str | None = None
    ip_address: str | None = None

    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expires_at

    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_valid(self) -> bool:
        return not self.is_expired() and not self.is_revoked()

    def revoke(self) -> "RefreshToken":
        return self.model_copy(update={"revoked_at": datetime.now(UTC)})
