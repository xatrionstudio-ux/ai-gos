"""
AI-GOS Core Package
Shared domain primitives: entities, repositories, results, pagination, exceptions.
"""

from .base_entity import AggregateRoot, BaseEntity
from .base_repository import BaseRepository
from .exceptions import (
    AIGOSException,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .pagination import CursorPage, OffsetPage, PaginationParams
from .result import Err, Ok, Result

__all__ = [
    "BaseEntity",
    "AggregateRoot",
    "BaseRepository",
    "AIGOSException",
    "NotFoundError",
    "ConflictError",
    "AuthorizationError",
    "ValidationError",
    "RateLimitError",
    "Ok",
    "Err",
    "Result",
    "PaginationParams",
    "OffsetPage",
    "CursorPage",
]
