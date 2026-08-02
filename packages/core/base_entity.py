"""
Base domain entity and aggregate root.

Entities have identity and lifecycle. Aggregate roots own consistency boundaries.
All entities are immutable by convention — use model_copy(update=...) to create
updated versions rather than mutating in place.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseEntity(BaseModel):
    """
    Base class for all domain entities.

    Entities are compared by identity (id), not by value.
    Fields are frozen by default — create new instances via model_copy(update={}).
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def with_update(self, **changes: Any) -> "BaseEntity":
        """Return a new entity with the given fields updated, bumping updated_at."""
        return self.model_copy(update={**changes, "updated_at": datetime.now(UTC)})


class AggregateRoot(BaseEntity):
    """
    Aggregate root — owns a consistency boundary.

    Collects domain events during its lifecycle. Events are cleared after
    being dispatched by the event bus.
    """

    model_config = ConfigDict(frozen=False, arbitrary_types_allowed=True)

    _domain_events: list[Any] = []

    def add_event(self, event: Any) -> None:
        """Stage a domain event for dispatch."""
        self._domain_events.append(event)

    def pull_events(self) -> list[Any]:
        """Return all staged events and clear the buffer."""
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def has_events(self) -> bool:
        return len(self._domain_events) > 0
