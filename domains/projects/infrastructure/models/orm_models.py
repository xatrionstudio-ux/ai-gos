"""
SQLAlchemy ORM model for Projects domain.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import BOOLEAN, Column, ForeignKey, TEXT, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from domains.identity.infrastructure.models.orm_models import BaseORM


class ProjectModel(BaseORM):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    website_url: Mapped[str] = mapped_column(TEXT, nullable=False)
    brand_voice: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    seo_strategy: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    cms_config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(TEXT, nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
