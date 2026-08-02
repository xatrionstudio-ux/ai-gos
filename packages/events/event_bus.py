"""
Event Bus — dispatches domain events to subscribers via Redis pub/sub and Celery tasks.

Architecture:
- Domain events are persisted to PostgreSQL (domain_events table) first
- Then dispatched to Redis pub/sub for real-time consumers
- And queued as Celery tasks for durable async processing
- Replays are possible from the domain_events table

This dual-dispatch ensures:
1. No events are lost (DB is source of truth)
2. Real-time delivery for SSE streams
3. Reliable processing via Celery's retry semantics
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

from .event_schema import DomainEvent

if TYPE_CHECKING:
    import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# Registry of event type → list of async handler coroutines (in-process)
_HANDLERS: dict[str, list[Callable]] = {}


def subscribe(event_type: str) -> Callable:
    """
    Decorator to register an in-process event handler.

    Usage:
        @subscribe("knowledge.document.ingested")
        async def handle_ingested(event: KnowledgeDocumentIngested) -> None:
            ...
    """
    def decorator(fn: Callable) -> Callable:
        if event_type not in _HANDLERS:
            _HANDLERS[event_type] = []
        _HANDLERS[event_type].append(fn)
        logger.debug("Registered handler %s for event %s", fn.__name__, event_type)
        return fn
    return decorator


class EventBus:
    """
    Central event dispatcher.

    Responsibilities:
    1. Persist event to domain_events table (via repository)
    2. Publish to Redis pub/sub channel
    3. Dispatch Celery task for durable processing
    4. Call in-process handlers for immediate side effects
    """

    def __init__(
        self,
        redis_client: "aioredis.Redis",
        celery_app: object | None = None,
        event_repository: object | None = None,
    ) -> None:
        self._redis = redis_client
        self._celery = celery_app
        self._event_repo = event_repository

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event.

        Order of operations:
        1. Persist to DB (durable, replayable)
        2. Publish to Redis pub/sub (real-time)
        3. Dispatch Celery task (reliable async)
        4. Call in-process handlers (immediate)
        """
        # 1. Persist
        if self._event_repo:
            try:
                await self._event_repo.save(event)
            except Exception:
                logger.exception("Failed to persist event %s", event.id)
                raise

        # 2. Redis pub/sub
        try:
            channel = f"aigos:events:{event.event_type}"
            await self._redis.publish(channel, event.to_json())
        except Exception:
            logger.exception("Failed to publish event %s to Redis", event.id)
            # Don't raise — Redis is best-effort for real-time; DB is durable

        # 3. Celery task dispatch
        if self._celery:
            try:
                self._celery.send_task(
                    "events.process_domain_event",
                    args=[event.model_dump(mode="json")],
                    queue="default",
                    countdown=0,
                    retry=True,
                    retry_policy={
                        "max_retries": 5,
                        "interval_start": 1,
                        "interval_step": 2,
                        "interval_max": 30,
                    },
                )
            except Exception:
                logger.exception("Failed to dispatch Celery task for event %s", event.id)

        # 4. In-process handlers
        handlers = _HANDLERS.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                logger.exception(
                    "In-process handler %s failed for event %s",
                    handler.__name__,
                    event.id,
                )

        logger.info(
            "Event dispatched",
            extra={
                "event_id": str(event.id),
                "event_type": event.event_type,
                "aggregate_id": str(event.aggregate_id),
                "org_id": str(event.org_id) if event.org_id else None,
            },
        )

    async def publish_many(self, events: list[DomainEvent]) -> None:
        """Batch publish multiple events."""
        for event in events:
            await self.publish(event)
