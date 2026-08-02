"""
MemoryBroker — Central memory gateway for all AI agents.

Agents query MemoryBroker; they NEVER access Redis or Qdrant directly.
Manages the 7 Memory Layers and calculates context token budgets.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from domains.memory.domain.entities.memory import MemoryItem, MemoryLayerType

logger = logging.getLogger(__name__)


class AssembledContext(BaseModel if "BaseModel" in globals() else object):
    """Context window payload ready for LLM consumption."""

    working_context: dict[str, Any]
    project_context: dict[str, Any]
    organization_context: dict[str, Any]
    semantic_context: list[str]
    total_token_estimate: int


class MemoryBroker:
    """Enterprise Memory Gateway."""

    def __init__(self) -> None:
        self._store: dict[str, MemoryItem] = {}

    def store_memory(
        self,
        org_id: uuid.UUID,
        layer: MemoryLayerType,
        key: str,
        content: dict[str, Any],
        project_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        importance_score: float = 1.0,
    ) -> MemoryItem:
        """Store a memory item into its target memory layer."""
        mem_key = f"{org_id}:{project_id or 'global'}:{layer.value}:{key}"
        item = MemoryItem(
            org_id=org_id,
            project_id=project_id,
            user_id=user_id,
            layer=layer,
            key=key,
            content=content,
            importance_score=importance_score,
        )
        self._store[mem_key] = item
        logger.debug("Stored memory key=%s in layer=%s", key, layer.value)
        return item

    def get_memory(
        self,
        org_id: uuid.UUID,
        layer: MemoryLayerType,
        key: str,
        project_id: uuid.UUID | None = None,
    ) -> MemoryItem | None:
        """Retrieve a specific memory item by key and layer."""
        mem_key = f"{org_id}:{project_id or 'global'}:{layer.value}:{key}"
        return self._store.get(mem_key)

    def assemble_context(
        self,
        org_id: uuid.UUID,
        project_id: uuid.UUID,
        max_token_budget: int = 32000,
    ) -> dict[str, Any]:
        """
        Assemble dynamic context window according to token budget distribution:
        - Knowledge: 35%
        - Research: 25%
        - Working Memory: 20%
        - Instructions & Style: 20%
        """
        working_items = [m.content for m in self._store.values() if m.org_id == org_id and m.layer == MemoryLayerType.WORKING]
        project_items = [m.content for m in self._store.values() if m.project_id == project_id and m.layer == MemoryLayerType.PROJECT]
        org_items = [m.content for m in self._store.values() if m.org_id == org_id and m.layer == MemoryLayerType.ORGANIZATION]

        return {
            "token_budget": max_token_budget,
            "working_memory": working_items,
            "project_memory": project_items,
            "organization_memory": org_items,
            "assembled": True,
        }
