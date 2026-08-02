"""
Product Knowledge Layer (PKL) Domain Entities.

The Single Source of Truth for product capabilities, features, personas, and workflows.
No AI agent is ever allowed to generate content without referencing these entities.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone

UTC = timezone.utc
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from core.base_entity import AggregateRoot, BaseEntity


class DocumentType(StrEnum):
    FEATURE = "feature"
    FAQ = "faq"
    CHANGELOG = "changelog"
    API_DOC = "api_doc"
    LANDING_PAGE = "landing_page"
    INTEGRATION = "integration"
    PERSONA = "persona"
    COMPETITOR = "competitor"
    SUPPORT_TICKET = "support_ticket"


class EntityType(StrEnum):
    FEATURE = "feature"
    INTEGRATION = "integration"
    COMPETITOR = "competitor"
    PERSONA = "persona"
    WORKFLOW_STAGE = "workflow_stage"
    COMPLIANCE_RULE = "compliance_rule"


class KnowledgeSource(BaseEntity):
    """Configuration for an ingested knowledge source."""

    project_id: uuid.UUID
    source_type: str  # 'website','notion','github','markdown','pdf'...
    source_url: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    last_synced_at: datetime | None = None
    sync_frequency_minutes: int = Field(default=60)
    is_active: bool = Field(default=True)


class KnowledgeDocument(AggregateRoot):
    """Parsed and versioned document in the Knowledge Layer."""

    project_id: uuid.UUID
    source_id: uuid.UUID | None = None
    title: str
    content: str
    content_hash: str  # SHA-256 for deduplication
    document_type: DocumentType
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: int = Field(default=1)
    is_current: bool = Field(default=True)

    @classmethod
    def create(
        cls,
        project_id: uuid.UUID,
        title: str,
        content: str,
        document_type: DocumentType,
        source_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "KnowledgeDocument":
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return cls(
            project_id=project_id,
            source_id=source_id,
            title=title,
            content=content,
            content_hash=content_hash,
            document_type=document_type,
            metadata=metadata or {},
        )


class KnowledgeChunk(BaseEntity):
    """Text chunk created from a KnowledgeDocument for vector indexing."""

    document_id: uuid.UUID
    project_id: uuid.UUID
    chunk_index: int
    content: str
    token_count: int
    embedding_model: str = "text-embedding-3-large"
    qdrant_point_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeEntity(BaseEntity):
    """Extracted product entity (e.g. Feature, Competitor, Persona)."""

    project_id: uuid.UUID
    entity_type: EntityType
    name: str
    description: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    source_document_ids: list[uuid.UUID] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
