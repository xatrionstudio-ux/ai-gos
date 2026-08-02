"""
SQLAlchemy ORM models for Identity domain.

These models map directly to PostgreSQL tables.
Domain entities (User, Organization, Role) convert to/from these models.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any

from sqlalchemy import (
    BOOLEAN,
    DATETIME,
    INTEGER,
    JSON,
    STRING,
    TEXT,
    TIMESTAMP,
    Column,
    ForeignKey,
    Index,
    Table,,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseORM(DeclarativeBase):
    """Declarative Base for SQLAlchemy ORM."""
    pass


user_roles_table = Table(
    "user_roles",
    BaseORM.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class OrganizationModel(BaseORM):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    slug: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(TEXT, nullable=False, default="starter")
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    users: Mapped[list["UserModel"]] = relationship("UserModel", back_populates="organization", cascade="all, delete-orphan")
    roles: Mapped[list["RoleModel"]] = relationship("RoleModel", back_populates="organization", cascade="all, delete-orphan")


class RoleModel(BaseORM):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    permissions: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    organization: Mapped["OrganizationModel"] = relationship("OrganizationModel", back_populates="roles")
    users: Mapped[list["UserModel"]] = relationship("UserModel", secondary=user_roles_table, back_populates="roles")

    __table_args__ = (
        UniqueConstraint("org_id", "name", name="uq_roles_org_name"),
    )


class UserModel(BaseORM):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(TEXT, nullable=False, index=True)
    email_verified: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    hashed_password: Mapped[str] = mapped_column(TEXT, nullable=False)
    full_name: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    last_login: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    organization: Mapped["OrganizationModel"] = relationship("OrganizationModel", back_populates="users")
    roles: Mapped[list["RoleModel"]] = relationship("RoleModel", secondary=user_roles_table, back_populates="users")
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship("RefreshTokenModel", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("org_id", "email", name="uq_users_org_email"),
    )


class RefreshTokenModel(BaseORM):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="refresh_tokens")
