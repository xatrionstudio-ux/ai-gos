"""
Celery Task Processing Engine for AI-GOS.

Queues:
- default: General system tasks
- knowledge: Parsing, chunking, embedding, entity extraction
- research: SERP crawling, competitor research, evidence collection
- content: Writing, SEO optimization, schema generation
- publishing: CMS adapters, webhook delivery
- analytics: Traffic monitoring, content decay detection
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add monorepo package & domain paths to sys.path for cloud deployment compatibility
_root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root_dir))
sys.path.insert(0, str(_root_dir / "packages"))
sys.path.insert(0, str(_root_dir / "domains"))

logger = logging.getLogger("ai-gos-worker")

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/2")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/3")

celery_app = Celery(
    "ai-gos-worker",
    broker=broker_url,
    backend=result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 mins soft limit
    worker_prefetch_multiplier=1,  # Prevent task hoarding
    task_acks_late=True,  # Re-queue on worker crash
    task_reject_on_worker_lost=True,
    task_routes={
        "events.process_domain_event": {"queue": "default"},
        "knowledge.*": {"queue": "knowledge"},
        "research.*": {"queue": "research"},
        "content.*": {"queue": "content"},
        "publishing.*": {"queue": "publishing"},
        "analytics.*": {"queue": "analytics"},
    },
)


@celery_app.task(name="events.process_domain_event", bind=True, max_retries=5)
def process_domain_event(self, event_data: dict) -> dict:
    """Process a domain event asynchronously with retries."""
    logger.info("Processing domain event: %s", event_data.get("event_type"))
    return {"status": "processed", "event_id": event_data.get("id")}
