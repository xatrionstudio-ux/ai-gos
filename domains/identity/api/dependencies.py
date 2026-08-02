"""
FastAPI Dependencies for Authentication, Tenant Isolation, and RBAC.

Used by all domain API routers to enforce authentication and authorization.

Usage:
    @router.get("/protected")
    async def my_endpoint(
        user: User = Depends(get_current_user),
        _: None = Depends(require_permission(Permission.PROJECTS_READ))
    ):
        ...
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from domains.identity.domain.entities.user import Permission, User
from domains.identity.infrastructure.adapters.jwt_service import JWTService, TokenPayload
from domains.identity.infrastructure.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

_security = HTTPBearer(auto_error=True)
_jwt_service = JWTService()


async def get_db_session() -> AsyncSession:
    """Placeholder dependency — overridden at FastAPI app initialization."""
    raise NotImplementedError("Database session dependency not registered.")


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(_security)]
) -> TokenPayload:
    """Extract and decode RS256 JWT access token."""
    try:
        return _jwt_service.decode_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired access token."},
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    payload: Annotated[TokenPayload, Depends(get_token_payload)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """
    Load current User entity from database and attach resolved permissions.

    Enforces active user check.
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(payload.user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_INACTIVE", "message": "User account is disabled or deleted."},
        )

    # Cross-check tenant isolation
    if user.org_id != payload.org_id:
        logger.error(
            "Tenant isolation mismatch! user.org_id=%s, payload.org_id=%s",
            user.org_id,
            payload.org_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "TENANT_MISMATCH", "message": "Cross-tenant access violation."},
        )

    return user


def require_permission(permission: Permission) -> Callable:
    """
    Dependency factory enforcing a required RBAC permission.

    Raises 403 Forbidden if current user lacks the permission.
    """
    async def permission_checker(
        user: Annotated[User, Depends(get_current_user)]
    ) -> None:
        if not user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": f"Permission '{permission}' is required for this endpoint.",
                },
            )

    return permission_checker
