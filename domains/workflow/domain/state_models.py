"""
Typed Pydantic State Models for LangGraph workflows.

No raw dictionaries! Each domain aspect has its own immutable, typed state class.
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

from pydantic import BaseModel, ConfigDict, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class WorkflowStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMED_OUT = "timed_out"


# ─── Individual Bounded States ────────────────────────────────────────────────

class ProjectState(BaseModel):
    model_config = ConfigDict(frozen=True)
    project_id: uuid.UUID
    org_id: uuid.UUID
    name: str
    website_url: str
    brand_voice: dict[str, Any] = Field(default_factory=dict)
    seo_strategy: dict[str, Any] = Field(default_factory=dict)


class KnowledgeState(BaseModel):
    model_config = ConfigDict(frozen=True)
    document_ids: list[uuid.UUID] = Field(default_factory=list)
    relevant_chunks: list[dict[str, Any]] = Field(default_factory=list)
    extracted_entities: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=1.0)


class ResearchState(BaseModel):
    model_config = ConfigDict(frozen=True)
    query: str = ""
    serp_results: list[dict[str, Any]] = Field(default_factory=list)
    competitor_insights: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=1.0)


class SEOState(BaseModel):
    model_config = ConfigDict(frozen=True)
    keyword: str = ""
    search_volume: int = 0
    difficulty: float = 0.0
    intent: str = "informational"
    cluster_name: str | None = None
    target_word_count: int = 2000
    schema_types: list[str] = Field(default_factory=lambda: ["Article", "FAQPage"])


class ArticleOutline(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: str
    meta_description: str
    sections: list[dict[str, Any]] = Field(default_factory=list)  # H2/H3 structures with bullet points


class ArticleDraft(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: str
    slug: str
    content_markdown: str
    word_count: int
    readability_score: float = 0.0
    brand_voice_score: float = 0.0
    fact_check_score: float = 0.0


class ContentState(BaseModel):
    model_config = ConfigDict(frozen=True)
    outline: ArticleOutline | None = None
    draft: ArticleDraft | None = None
    seo_score: float = 0.0
    schema_json: dict[str, Any] = Field(default_factory=dict)
    faq_list: list[dict[str, str]] = Field(default_factory=list)
    internal_links: list[dict[str, str]] = Field(default_factory=list)


class ApprovalState(BaseModel):
    model_config = ConfigDict(frozen=True)
    approval_id: uuid.UUID
    approval_type: str  # outline | research | writing | publishing | legal | brand
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    responded_at: datetime | None = None
    notes: str | None = None
    edited_data: dict[str, Any] | None = None


class PublishingState(BaseModel):
    model_config = ConfigDict(frozen=True)
    cms_type: str = "nextjs"
    published_url: str | None = None
    cms_post_id: str | None = None
    published_at: datetime | None = None


# ─── Root Aggregate Workflow State ───────────────────────────────────────────

class WorkflowState(BaseModel):
    """
    Combined aggregate state passed through LangGraph nodes.

    LangGraph nodes receive this state and return updated versions.
    """

    workflow_id: uuid.UUID
    workflow_type: str  # 'seo_content' | 'onboarding' | 'product_update' | 'refresh'
    thread_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_node: str = "start"

    project: ProjectState
    knowledge: KnowledgeState = Field(default_factory=lambda: KnowledgeState(document_ids=[]))
    research: ResearchState = Field(default_factory=lambda: ResearchState())
    seo: SEOState = Field(default_factory=lambda: SEOState())
    content: ContentState = Field(default_factory=lambda: ContentState())
    approval: ApprovalState | None = None
    publishing: PublishingState = Field(default_factory=lambda: PublishingState())

    error_message: str | None = None
    retry_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
