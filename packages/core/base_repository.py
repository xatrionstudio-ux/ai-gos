"""
Repository port (interface) for all domains.

Concrete implementations live in the infrastructure layer (SQLAlchemy adapters).
Business logic depends on this abstract interface only — never on SQLAlchemy directly.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .base_entity import BaseEntity
from .pagination import OffsetPage, PaginationParams

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(ABC, Generic[T]):
    """
    Generic repository port.

    All methods are async — repositories always wrap async DB sessions.
    """

    @abstractmethod
    async def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        """Fetch a single entity by primary key. Returns None if not found."""
        ...

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Persist a new or updated entity. Returns the saved entity."""
        ...

    @abstractmethod
    async def delete(self, entity_id: uuid.UUID) -> bool:
        """Soft-delete or hard-delete an entity. Returns True if deleted."""
        ...

    @abstractmethod
    async def list(self, params: PaginationParams) -> OffsetPage[T]:
        """Paginated list with optional filters from params."""
        ...

    @abstractmethod
    async def exists(self, entity_id: uuid.UUID) -> bool:
        """Check existence without loading the full entity."""
        ...
