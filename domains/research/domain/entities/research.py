"""
Research Domain Entities.

Rule from specification:
- Research collects evidence. It NEVER writes articles.
- Memory is permanent: Every discovery is reusable knowledge. Never perform identical research twice.
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


class EvidenceSourceType(StrEnum):
    GOOGLE_SERP = "google_serp"
    BING_SERP = "bing_serp"
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    WIKIPEDIA = "wikipedia"
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    COMPETITOR_SITE = "competitor_site"
    PRODUCT_DOCS = "product_docs"
    GITHUB = "github"


class ResearchSession(AggregateRoot):
    """Aggregate representing a market/topic research session."""

    project_id: uuid.UUID
    keyword_id: uuid.UUID | None = None
    query: str
    sources_searched: list[EvidenceSourceType] = Field(default_factory=list)
    evidence_count: int = Field(default=0)
    confidence_score: float = Field(default=1.0)
    status: str = Field(default="pending")  # pending | running | done | failed
    completed_at: datetime | None = None


class Evidence(BaseEntity):
    """A verified snippet of evidence gathered from a external or internal source."""

    session_id: uuid.UUID
    source_url: str
    source_type: EvidenceSourceType
    title: str | None = None
    excerpt: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompetitorAnalysis(BaseEntity):
    """Competitive intelligence snippet."""

    project_id: uuid.UUID
    competitor_name: str
    competitor_url: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_features: list[str] = Field(default_factory=list)
    pricing_model: str | None = None
    confidence: float = Field(default=1.0)
