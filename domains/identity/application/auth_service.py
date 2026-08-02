"""
Identity Domain Application Service.

Encapsulates authentication & registration use cases.
Uses Result[T, E] monad for explicit error handling.
Does NOT deal with HTTP responses — returns domain entities or DTOs.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from core.exceptions import AuthenticationError, ConflictError, NotFoundError, ValidationError
from core.result import Err, Ok, Result
from events.event_bus import EventBus
from events.event_schema import UserLoggedIn, UserRegistered

from domains.identity.domain.entities.user import Organization, RefreshToken, Role, User
from domains.identity.infrastructure.adapters.jwt_service import JWTService
from domains.identity.infrastructure.adapters.password_hasher import PasswordHasherAdapter
from domains.identity.infrastructure.repositories.user_repository import (
    OrganizationRepository,
    RefreshTokenRepository,
    UserRepository,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegisterCommand:
    org_name: str
    org_slug: str
    email: str
    password: str
    full_name: str | None = None


@dataclass(frozen=True)
class LoginCommand:
    org_slug: str
    email: str
    password: str
    user_agent: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in_seconds: int = 900
    user_id: uuid.UUID = uuid.UUID(int=0)
    org_id: uuid.UUID = uuid.UUID(int=0)


class AuthService:
    """Application Service for Authentication & User Registration."""

    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        token_repo: RefreshTokenRepository,
        jwt_service: JWTService,
        event_bus: EventBus | None = None,
    ) -> None:
        self._user_repo = user_repo
        self._org_repo = org_repo
        self._token_repo = token_repo
        self._jwt = jwt_service
        self._event_bus = event_bus

    async def register_organization_and_owner(
        self, cmd: RegisterCommand
    ) -> Result[tuple[Organization, User, AuthTokens], Exception]:
        """
        Register a new Organization along with its first Owner user.
        """
        # Validate slug uniqueness
        existing_org = await self._org_repo.get_by_slug(cmd.org_slug)
        if existing_org:
            return Err(ConflictError(f"Organization slug '{cmd.org_slug}' is already taken."))

        # Create Organization
        org = Organization(
            name=cmd.org_name,
            slug=cmd.org_slug,
        )
        saved_org = await self._org_repo.save(org)

        # Create Owner User
        hashed_password = PasswordHasherAdapter.hash_password(cmd.password)
        user = User(
            org_id=saved_org.id,
            email=cmd.email,
            hashed_password=hashed_password,
            full_name=cmd.full_name,
            email_verified=False,
            is_superuser=True,  # First user of new org is admin/owner
        )
        saved_user = await self._user_repo.save(user)

        # Generate tokens
        tokens_res = await self._issue_tokens(saved_user, saved_org.id)

        # Dispatch event
        if self._event_bus:
            await self._event_bus.publish(
                UserRegistered(
                    aggregate_id=saved_user.id,
                    org_id=saved_org.id,
                    payload={"email": saved_user.email, "org_slug": saved_org.slug},
                )
            )

        return Ok((saved_org, saved_user, tokens_res))

    async def login(self, cmd: LoginCommand) -> Result[tuple[User, AuthTokens], Exception]:
        """Authenticate user credentials and return auth tokens."""
        org = await self._org_repo.get_by_slug(cmd.org_slug)
        if not org or not org.is_active:
            return Err(AuthenticationError("Invalid credentials or organization inactive."))

        user = await self._user_repo.get_by_email(org.id, cmd.email)
        if not user:
            return Err(AuthenticationError("Invalid credentials."))

        # Verify password
        if not PasswordHasherAdapter.verify_password(cmd.password, user.hashed_password):
            return Err(AuthenticationError("Invalid credentials."))

        user.verify_is_active()

        # Update last login
        updated_user = user.record_login()
        saved_user = await self._user_repo.save(updated_user)

        # Check if password hash needs rehash (security maintenance)
        if PasswordHasherAdapter.needs_rehash(user.hashed_password):
            new_hash = PasswordHasherAdapter.hash_password(cmd.password)
            saved_user = await self._user_repo.save(saved_user.update_password(new_hash))

        # Issue tokens
        tokens = await self._issue_tokens(saved_user, org.id, cmd.user_agent, cmd.ip_address)

        # Dispatch event
        if self._event_bus:
            await self._event_bus.publish(
                UserLoggedIn(
                    aggregate_id=saved_user.id,
                    org_id=org.id,
                    payload={"email": saved_user.email},
                )
            )

        return Ok((saved_user, tokens))

    async def refresh_tokens(
        self, raw_refresh_token: str, user_agent: str | None = None, ip_address: str | None = None
    ) -> Result[AuthTokens, Exception]:
        """Exchange a valid refresh token for a new access & refresh token pair."""
        token_hash = self._jwt.hash_refresh_token(raw_refresh_token)
        stored_token = await self._token_repo.get_by_hash(token_hash)

        if not stored_token or not stored_token.is_valid():
            return Err(AuthenticationError("Invalid or expired refresh token."))

        # Revoke used refresh token (refresh token rotation)
        await self._token_repo.save(stored_token.revoke())

        user = await self._user_repo.get_by_id(stored_token.user_id)
        if not user or not user.is_active:
            return Err(AuthenticationError("User account inactive or deleted."))

        new_tokens = await self._issue_tokens(user, stored_token.org_id, user_agent, ip_address)
        return Ok(new_tokens)

    async def logout(self, raw_refresh_token: str) -> Result[bool, Exception]:
        """Revoke a refresh token on logout."""
        token_hash = self._jwt.hash_refresh_token(raw_refresh_token)
        stored_token = await self._token_repo.get_by_hash(token_hash)
        if stored_token:
            await self._token_repo.save(stored_token.revoke())
        return Ok(True)

    async def _issue_tokens(
        self,
        user: User,
        org_id: uuid.UUID,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthTokens:
        """Internal helper to issue access and refresh tokens."""
        permissions_str = [p.value for p in user._resolved_permissions]
        access_token = self._jwt.create_access_token(
            user_id=user.id,
            org_id=org_id,
            email=user.email,
            is_superuser=user.is_superuser,
            permissions=permissions_str,
        )

        raw_refresh, token_hash = self._jwt.create_refresh_token()
        refresh_entity = RefreshToken(
            user_id=user.id,
            org_id=org_id,
            token_hash=token_hash,
            expires_at=self._jwt.get_refresh_expiry() + refresh_entity_now(),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await self._token_repo.save(refresh_entity)

        return AuthTokens(
            access_token=access_token,
            refresh_token=raw_refresh,
            expires_in_seconds=int(self._jwt.get_token_expiry().total_seconds()),
            user_id=user.id,
            org_id=org_id,
        )


def refresh_entity_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
