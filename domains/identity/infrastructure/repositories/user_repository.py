"""
SQLAlchemy repository implementations for Identity domain.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.base_repository import BaseRepository
from core.pagination import OffsetPage, PaginationParams
from domains.identity.domain.entities.user import Organization, Permission, RefreshToken, Role, User
from domains.identity.infrastructure.models.orm_models import (
    OrganizationModel,
    RefreshTokenModel,
    RoleModel,
    UserModel,
)


class UserRepository(BaseRepository[User]):
    """Async SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        role_ids = [r.id for r in model.roles]
        permissions: set[Permission] = set()
        for role in model.roles:
            for p in role.permissions:
                try:
                    permissions.add(Permission(p))
                except ValueError:
                    pass

        user = User(
            id=model.id,
            org_id=model.org_id,
            email=model.email,
            email_verified=model.email_verified,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            avatar_url=model.avatar_url,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            last_login=model.last_login,
            created_at=model.created_at,
            updated_at=model.updated_at,
            role_ids=role_ids,
        )
        user._resolved_permissions = list(permissions)
        return user

    async def get_by_id(self, entity_id: uuid.UUID) -> User | None:
        stmt = (
            select(UserModel)
            .where(UserModel.id == entity_id)
            .options(selectinload(UserModel.roles))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, org_id: uuid.UUID, email: str) -> User | None:
        stmt = (
            select(UserModel)
            .where(UserModel.org_id == org_id, UserModel.email == email.lower())
            .options(selectinload(UserModel.roles))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, entity: User) -> User:
        stmt = select(UserModel).where(UserModel.id == entity.id).options(selectinload(UserModel.roles))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            model = UserModel(
                id=entity.id,
                org_id=entity.org_id,
                email=entity.email.lower(),
                email_verified=entity.email_verified,
                hashed_password=entity.hashed_password,
                full_name=entity.full_name,
                avatar_url=entity.avatar_url,
                is_active=entity.is_active,
                is_superuser=entity.is_superuser,
                last_login=entity.last_login,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
            self._session.add(model)
        else:
            model.email = entity.email.lower()
            model.email_verified = entity.email_verified
            model.hashed_password = entity.hashed_password
            model.full_name = entity.full_name
            model.avatar_url = entity.avatar_url
            model.is_active = entity.is_active
            model.is_superuser = entity.is_superuser
            model.last_login = entity.last_login
            model.updated_at = entity.updated_at

        # Update roles if specified
        if entity.role_ids:
            roles_stmt = select(RoleModel).where(RoleModel.id.in_(entity.role_ids))
            roles_res = await self._session.execute(roles_stmt)
            model.roles = list(roles_res.scalars().all())

        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, entity_id: uuid.UUID) -> bool:
        stmt = delete(UserModel).where(UserModel.id == entity_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def list(self, params: PaginationParams) -> OffsetPage[User]:
        stmt = select(UserModel).options(selectinload(UserModel.roles)).offset(params.offset).limit(params.size)
        res = await self._session.execute(stmt)
        models = res.scalars().all()

        count_stmt = select(UserModel)
        count_res = await self._session.execute(count_stmt)
        total = len(count_res.scalars().all())

        items = [self._to_entity(m) for m in models]
        return OffsetPage.create(items=items, total=total, params=params)

    async def exists(self, entity_id: uuid.UUID) -> bool:
        stmt = select(UserModel.id).where(UserModel.id == entity_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none() is not None


class OrganizationRepository(BaseRepository[Organization]):
    """Async SQLAlchemy implementation of OrganizationRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: OrganizationModel) -> Organization:
        return Organization(
            id=model.id,
            name=model.name,
            slug=model.slug,
            plan=model.plan,
            settings=model.settings,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, entity_id: uuid.UUID) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.id == entity_id)
        res = await self._session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.slug == slug.lower())
        res = await self._session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, entity: Organization) -> Organization:
        stmt = select(OrganizationModel).where(OrganizationModel.id == entity.id)
        res = await self._session.execute(stmt)
        model = res.scalar_one_or_none()

        if not model:
            model = OrganizationModel(
                id=entity.id,
                name=entity.name,
                slug=entity.slug.lower(),
                plan=entity.plan,
                settings=entity.settings,
                is_active=entity.is_active,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
            self._session.add(model)
        else:
            model.name = entity.name
            model.slug = entity.slug.lower()
            model.plan = entity.plan
            model.settings = entity.settings
            model.is_active = entity.is_active
            model.updated_at = entity.updated_at

        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, entity_id: uuid.UUID) -> bool:
        stmt = delete(OrganizationModel).where(OrganizationModel.id == entity_id)
        res = await self._session.execute(stmt)
        return res.rowcount > 0

    async def list(self, params: PaginationParams) -> OffsetPage[Organization]:
        stmt = select(OrganizationModel).offset(params.offset).limit(params.size)
        res = await self._session.execute(stmt)
        models = res.scalars().all()

        items = [self._to_entity(m) for m in models]
        return OffsetPage.create(items=items, total=len(items), params=params)

    async def exists(self, entity_id: uuid.UUID) -> bool:
        stmt = select(OrganizationModel.id).where(OrganizationModel.id == entity_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none() is not None


class RefreshTokenRepository:
    """Async SQLAlchemy implementation of RefreshTokenRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            org_id=model.org_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            user_agent=model.user_agent,
            ip_address=model.ip_address,
            created_at=model.created_at,
        )

    async def save(self, entity: RefreshToken) -> RefreshToken:
        model = RefreshTokenModel(
            id=entity.id,
            user_id=entity.user_id,
            org_id=entity.org_id,
            token_hash=entity.token_hash,
            expires_at=entity.expires_at,
            revoked_at=entity.revoked_at,
            user_agent=entity.user_agent,
            ip_address=entity.ip_address,
            created_at=entity.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        res = await self._session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        from datetime import datetime, timezone
        UTC = timezone.utc
        stmt = (
            RefreshTokenModel.__table__.update()
            .where(RefreshTokenModel.user_id == user_id, RefreshTokenModel.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
        res = await self._session.execute(stmt)
        return res.rowcount
