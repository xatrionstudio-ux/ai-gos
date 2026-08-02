"""
Domain Event schemas — the contract for all inter-domain communication.

Events are immutable value objects. Every event has:
- id: unique identifier (UUID)
- event_type: dot-namespaced string (e.g., "knowledge.document.ingested")
- aggregate_type: what the event is about
- aggregate_id: which specific instance
- occurred_at: when it happened (UTC)
- payload: event-specific data
- metadata: tracing, tenant, correlation IDs

Events are serialized to JSON for persistence and Redis pub/sub.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DomainEvent(BaseModel):
    """Base class for all domain events. Immutable."""

    model_config = ConfigDict(frozen=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str  # e.g. "knowledge.document.ingested"
    aggregate_type: str  # e.g. "KnowledgeDocument"
    aggregate_id: uuid.UUID
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Tenant context — always propagated
    org_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None

    # Correlation / tracing
    correlation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    causation_id: uuid.UUID | None = None  # ID of the event/command that caused this
    trace_id: str | None = None  # OpenTelemetry trace ID

    # Event-specific data
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "DomainEvent":
        return cls.model_validate_json(data)


# ─── Identity Events ──────────────────────────────────────────────────────────

class UserRegistered(DomainEvent):
    event_type: str = "identity.user.registered"
    aggregate_type: str = "User"


class UserLoggedIn(DomainEvent):
    event_type: str = "identity.user.logged_in"
    aggregate_type: str = "User"


class OrganizationCreated(DomainEvent):
    event_type: str = "identity.organization.created"
    aggregate_type: str = "Organization"


# ─── Project Events ───────────────────────────────────────────────────────────

class ProjectCreated(DomainEvent):
    event_type: str = "projects.project.created"
    aggregate_type: str = "Project"


class ProjectDeleted(DomainEvent):
    event_type: str = "projects.project.deleted"
    aggregate_type: str = "Project"


# ─── Knowledge Events ─────────────────────────────────────────────────────────

class KnowledgeDocumentIngested(DomainEvent):
    event_type: str = "knowledge.document.ingested"
    aggregate_type: str = "KnowledgeDocument"


class KnowledgeDocumentEmbedded(DomainEvent):
    event_type: str = "knowledge.document.embedded"
    aggregate_type: str = "KnowledgeDocument"


class KnowledgeEntityExtracted(DomainEvent):
    event_type: str = "knowledge.entity.extracted"
    aggregate_type: str = "KnowledgeEntity"


class KnowledgeUpdated(DomainEvent):
    event_type: str = "knowledge.updated"
    aggregate_type: str = "Project"


# ─── Research Events ──────────────────────────────────────────────────────────

class ResearchSessionStarted(DomainEvent):
    event_type: str = "research.session.started"
    aggregate_type: str = "ResearchSession"


class ResearchSessionCompleted(DomainEvent):
    event_type: str = "research.session.completed"
    aggregate_type: str = "ResearchSession"


class ResearchEvidenceCollected(DomainEvent):
    event_type: str = "research.evidence.collected"
    aggregate_type: str = "ResearchSession"


# ─── SEO Events ───────────────────────────────────────────────────────────────

class KeywordDiscovered(DomainEvent):
    event_type: str = "seo.keyword.discovered"
    aggregate_type: str = "Keyword"


class ClusterBuilt(DomainEvent):
    event_type: str = "seo.cluster.built"
    aggregate_type: str = "KeywordCluster"


class KeywordLost(DomainEvent):
    event_type: str = "seo.keyword.lost"
    aggregate_type: str = "Keyword"


# ─── Content Events ───────────────────────────────────────────────────────────

class ArticleCreated(DomainEvent):
    event_type: str = "content.article.created"
    aggregate_type: str = "Article"


class ArticleDraftCompleted(DomainEvent):
    event_type: str = "content.article.draft_completed"
    aggregate_type: str = "Article"


class ArticleApproved(DomainEvent):
    event_type: str = "content.article.approved"
    aggregate_type: str = "Article"


class ArticlePublished(DomainEvent):
    event_type: str = "content.article.published"
    aggregate_type: str = "Article"


class ArticleUpdated(DomainEvent):
    event_type: str = "content.article.updated"
    aggregate_type: str = "Article"


# ─── Workflow Events ──────────────────────────────────────────────────────────

class WorkflowStarted(DomainEvent):
    event_type: str = "workflow.started"
    aggregate_type: str = "Workflow"


class WorkflowCompleted(DomainEvent):
    event_type: str = "workflow.completed"
    aggregate_type: str = "Workflow"


class WorkflowFailed(DomainEvent):
    event_type: str = "workflow.failed"
    aggregate_type: str = "Workflow"


class WorkflowPaused(DomainEvent):
    event_type: str = "workflow.paused"
    aggregate_type: str = "Workflow"


class WorkflowResumed(DomainEvent):
    event_type: str = "workflow.resumed"
    aggregate_type: str = "Workflow"


class ApprovalRequested(DomainEvent):
    event_type: str = "workflow.approval.requested"
    aggregate_type: str = "Approval"


class ApprovalCompleted(DomainEvent):
    event_type: str = "workflow.approval.completed"
    aggregate_type: str = "Approval"


# ─── Analytics Events ─────────────────────────────────────────────────────────

class TrafficDropDetected(DomainEvent):
    event_type: str = "analytics.traffic.dropped"
    aggregate_type: str = "Article"


class ContentDecayDetected(DomainEvent):
    event_type: str = "analytics.content.decayed"
    aggregate_type: str = "Article"


class CompetitorChangedDetected(DomainEvent):
    event_type: str = "analytics.competitor.changed"
    aggregate_type: str = "Project"


# ─── Publishing Events ────────────────────────────────────────────────────────

class ArticlePublishedToCMS(DomainEvent):
    event_type: str = "publishing.article.published_to_cms"
    aggregate_type: str = "Publication"


class PublishingFailed(DomainEvent):
    event_type: str = "publishing.article.failed"
    aggregate_type: str = "Publication"


# ─── Feature / Product Events ─────────────────────────────────────────────────

class FeatureDetected(DomainEvent):
    event_type: str = "knowledge.feature.detected"
    aggregate_type: str = "KnowledgeEntity"


class ReleasePublished(DomainEvent):
    event_type: str = "knowledge.release.published"
    aggregate_type: str = "Project"
