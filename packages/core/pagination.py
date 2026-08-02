"""
Pagination models — offset-based and cursor-based.

Supports both patterns to handle different query needs:
- OffsetPage: simple page/size, good for fixed-order lists
- CursorPage: opaque cursor, good for infinite scroll and real-time feeds
"""

from __future__ import annotations

import base64
import json
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100


class PaginationParams(BaseModel):
    """Query params for paginated list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    size: int = Field(
        default=_DEFAULT_PAGE_SIZE,
        ge=1,
        le=_MAX_PAGE_SIZE,
        description="Items per page",
    )
    cursor: str | None = Field(default=None, description="Cursor for cursor-based pagination")
    order_by: str = Field(default="created_at", description="Sort field")
    order_dir: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort direction")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class OffsetPage(BaseModel, Generic[T]):
    """Standard paginated response."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, params: PaginationParams) -> "OffsetPage[T]":
        pages = max(1, -(-total // params.size))  # ceiling division
        return cls(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            pages=pages,
        )


class CursorPage(BaseModel, Generic[T]):
    """Cursor-based paginated response — stable under concurrent inserts."""

    items: list[T]
    next_cursor: str | None
    has_more: bool

    @staticmethod
    def encode_cursor(data: dict) -> str:
        payload = json.dumps(data, separators=(",", ":"))
        return base64.urlsafe_b64encode(payload.encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> dict:
        try:
            payload = base64.urlsafe_b64decode(cursor.encode()).decode()
            return json.loads(payload)
        except Exception as exc:
            from .exceptions import ValidationError

            raise ValidationError("Invalid pagination cursor.") from exc
