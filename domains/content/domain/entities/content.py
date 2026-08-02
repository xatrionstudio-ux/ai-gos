"""
Content Domain Entities.

Artifact Aggregate:
Represents generated outputs (Blog Posts, Landing Pages, FAQs, API Docs, Changelogs).
Rule: An Artifact MUST be associated with a specific, verified version of Knowledge.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

UTC = timezone.utc
from enum import Enum

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        pass
from typing import Any

from pydantic import BaseModel, Field

from core.base_entity import AggregateRoot, BaseEntity


class ArtifactType(StrEnum):
    BLOG_POST = "blog_post"
    LANDING_PAGE = "landing_page"
    FAQ = "faq"
    API_DOC = "api_doc"
    CASE_STUDY = "case_study"
    COMPARISON_PAGE = "comparison_page"
    CHANGELOG = "changelog"
    NEWSLETTER = "newsletter"
    SOCIAL_POST = "social_post"
    RELEASE_NOTE = "release_note"


class ArtifactStatus(StrEnum):
    DRAFT = "draft"
    RESEARCH = "research"
    OUTLINE = "outline"
    WRITING = "writing"
    REVIEW = "review"
    SEO = "seo"
    WAITING_APPROVAL = "waiting_approval"
    PUBLISHED = "published"
    MONITORING = "monitoring"
    REFRESHING = "refreshing"
    ARCHIVED = "archived"


class Article(AggregateRoot):
    """Artifact aggregate root representing a generated content piece."""

    project_id: uuid.UUID
    knowledge_version: int = Field(default=1, description="Strict reference to PKL knowledge version")
    keyword_id: uuid.UUID | None = None
    cluster_id: uuid.UUID | None = None
    title: str
    slug: str
    artifact_type: ArtifactType = ArtifactType.BLOG_POST
    status: ArtifactStatus = ArtifactStatus.DRAFT
    word_count: int = 0
    seo_score: float = Field(default=0.0, ge=0.0, le=100.0)
    readability_score: float = Field(default=0.0, ge=0.0, le=100.0)
    brand_score: float = Field(default=0.0, ge=0.0, le=100.0)
    fact_check_score: float = Field(default=0.0, ge=0.0, le=100.0)
    jsonld_schema: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    published_at: datetime | None = None


class ArticleVersion(BaseEntity):
    """Immutable version of an Article created during workflow steps."""

    article_id: uuid.UUID
    version: int
    content_markdown: str
    content_html: str | None = None
    author_agent: str  # e.g., 'WriterAgent'
    prompt_version: str
    model_used: str
    tokens_used: int = 0
    cost_usd: float = 0.0
    workflow_id: uuid.UUID | None = None
    trace_id: str | None = None
