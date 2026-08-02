"""
7-Layer Memory Engine Entities.
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

from core.base_entity import BaseEntity


class MemoryLayerType(StrEnum):
    WORKING = "working"          # Active workflow state (TTL: 1h)
    EPISODIC = "episodic"        # Historical events & traffic outcomes
    SEMANTIC = "semantic"        # High-dimensional concepts & product ontology
    PROCEDURAL = "procedural"    # Execution recipes & workflow templates
    PROJECT = "project"          # Brand voice, ICP personas, project rules
    ORGANIZATION = "organization"# Cross-project style guide & legal policy
    USER = "user"                # Individual user preferences


class MemoryItem(BaseEntity):
    """Memory item aggregate stored and queried via MemoryBroker."""

    org_id: uuid.UUID
    project_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    layer: MemoryLayerType
    key: str
    content: dict[str, Any]
    importance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    embedding_id: uuid.UUID | None = None
    expires_at: datetime | None = None
